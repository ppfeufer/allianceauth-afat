"""
Tasks
"""

# Standard Library
from datetime import timedelta

# Third Party
from bravado.exception import HTTPNotFound
from celery import shared_task

# Django
from django.utils import timezone

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger
from allianceauth.services.tasks import QueueOnce
from esi.models import Token

# Alliance Auth (External Libs)
from app_utils.esi import fetch_esi_status
from app_utils.logging import LoggerAddTag

# Alliance Auth AFAT
from afat import __title__
from afat.models import Fat, FatLink, Log, Setting
from afat.providers import esi
from afat.utils import get_or_create_character

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


ESI_ERROR_LIMIT = 50
ESI_TIMEOUT_ONCE_ERROR_LIMIT_REACHED = 60
ESI_MAX_RETRIES = 3
ESI_MAX_ERROR_COUNT = 3
ESI_ERROR_GRACE_TIME = 75

TASK_TIME_LIMIT = 120  # Stop after 2 minutes

# Params for all tasks
TASK_DEFAULT_KWARGS = {"time_limit": TASK_TIME_LIMIT, "max_retries": ESI_MAX_RETRIES}


@shared_task(**{**TASK_DEFAULT_KWARGS}, **{"base": QueueOnce})
def process_fats(data_list, data_source: str, fatlink_hash: str):
    """
    Due to the large possible size of fatlists,
    this process will be scheduled to process esi data
    and possible other sources in the future.

    :param data_list:
    :type data_list:
    :param data_source:
    :type data_source:
    :param fatlink_hash:
    :type fatlink_hash:
    :return:
    :rtype:
    """

    logger.debug(f"Data Source: {data_source}")

    if data_source == "esi":
        logger.info(
            msg=(
                f'Valid fleet for FAT link hash "{fatlink_hash}" found '
                "registered via ESI, checking for new pilots"
            )
        )

        for char in data_list:
            process_character.delay(
                character_id=char["character_id"],
                solar_system_id=char["solar_system_id"],
                ship_type_id=char["ship_type_id"],
                fatlink_hash=fatlink_hash,
            )


@shared_task
def process_character(
    character_id: int, solar_system_id: int, ship_type_id: int, fatlink_hash: str
):
    """
    Process character

    :param character_id:
    :param solar_system_id:
    :param ship_type_id:
    :param fatlink_hash:
    :return:
    """

    character = get_or_create_character(character_id=character_id)
    link = FatLink.objects.get(hash=fatlink_hash)

    solar_system = esi.client.Universe.get_universe_systems_system_id(
        system_id=solar_system_id
    ).result()
    ship = esi.client.Universe.get_universe_types_type_id(type_id=ship_type_id).result()

    solar_system_name = solar_system["name"]
    ship_name = ship["name"]

    fat, created = Fat.objects.get_or_create(
        fatlink=link,
        character=character,
        defaults={"system": solar_system_name, "shiptype": ship_name},
    )

    if created is True:
        logger.info(
            msg=(
                f"New Pilot: Adding {character} in {solar_system_name} flying "
                f'a {ship_name} to FAT link "{fatlink_hash}" (FAT ID {fat.pk})'
            )
        )

        return

    logger.debug(
        msg=(
            f"Pilot {character} already registered for FAT link {fatlink_hash} "
            f"with FAT ID {fat.pk}"
        )
    )


def _close_esi_fleet(fatlink: FatLink, reason: str) -> None:
    """
    Closing ESI fleet

    :param fatlink:
    :type fatlink:
    :param reason:
    :type reason:
    :return:
    :rtype:
    """

    logger.info(
        msg=f'Closing ESI FAT link with hash "{fatlink.hash}". Reason: {reason}'
    )

    fatlink.is_registered_on_esi = False
    fatlink.save()


def _esi_fatlinks_error_handling(error_key: str, fatlink: FatLink) -> None:
    """
    ESI error handling

    :param cache_key:
    :type cache_key:
    :param fatlink:
    :type fatlink:
    :return:
    :rtype:
    """

    time_now = timezone.now()

    # Close ESI fleet if the consecutive error count is too high
    if (
        fatlink.last_esi_error == error_key
        and fatlink.last_esi_error_time
        >= (time_now - timedelta(seconds=ESI_ERROR_GRACE_TIME))
        and fatlink.esi_error_count >= ESI_MAX_ERROR_COUNT
    ):
        _close_esi_fleet(fatlink=fatlink, reason=error_key.label)

        return

    error_count = (
        fatlink.esi_error_count + 1
        if fatlink.last_esi_error == error_key
        and fatlink.last_esi_error_time
        >= (time_now - timedelta(seconds=ESI_ERROR_GRACE_TIME))
        else 1
    )

    logger.info(
        msg=(
            f'FAT link "{fatlink.hash}" Error: "{error_key.label}" '
            f"({error_count} of {ESI_MAX_ERROR_COUNT})."
        )
    )

    fatlink.esi_error_count = error_count
    fatlink.last_esi_error = error_key
    fatlink.last_esi_error_time = time_now
    fatlink.save()


def _check_for_esi_fleet(fatlink: FatLink):
    required_scopes = ["esi-fleets.read_fleet.v1"]

    # Check if there is a fleet
    try:
        fleet_commander_id = fatlink.character.character_id
        esi_token = Token.get_token(
            character_id=fleet_commander_id, scopes=required_scopes
        )

        fleet_from_esi = esi.client.Fleets.get_characters_character_id_fleet(
            character_id=fleet_commander_id,
            token=esi_token.valid_access_token(),
        ).result()

        return {"fleet": fleet_from_esi, "token": esi_token}
    except HTTPNotFound:
        _esi_fatlinks_error_handling(
            error_key=FatLink.EsiError.NOT_IN_FLEET, fatlink=fatlink
        )
    except Exception:  # pylint: disable=broad-exception-caught
        _esi_fatlinks_error_handling(
            error_key=FatLink.EsiError.NO_FLEET, fatlink=fatlink
        )

    return False


def _process_esi_fatlink(fatlink: FatLink):
    """
    Processing ESI FAT link

    :param fatlink:
    :type fatlink:
    :return:
    :rtype:
    """

    logger.info(msg=f'Processing ESI FAT link with hash "{fatlink.hash}"')

    if fatlink.creator.profile.main_character is not None:
        # Check if there is a fleet
        esi_fleet = _check_for_esi_fleet(fatlink=fatlink)

        # We have a valid fleet result from ESI
        if esi_fleet and fatlink.esi_fleet_id == esi_fleet["fleet"]["fleet_id"]:
            # Check if we deal with the fleet boss here
            try:
                esi_fleet_member = esi.client.Fleets.get_fleets_fleet_id_members(
                    fleet_id=esi_fleet["fleet"]["fleet_id"],
                    token=esi_fleet["token"].valid_access_token(),
                ).result()
            except Exception:  # pylint: disable=broad-exception-caught
                _esi_fatlinks_error_handling(
                    error_key=FatLink.EsiError.NOT_FLEETBOSS, fatlink=fatlink
                )

            # Process fleet members
            else:
                logger.debug(
                    msg=(
                        "Processing fleet members for ESI FAT link with "
                        f'hash "{fatlink.hash}"'
                    )
                )

                process_fats.delay(
                    data_list=esi_fleet_member,
                    data_source="esi",
                    fatlink_hash=fatlink.hash,
                )
        else:
            _esi_fatlinks_error_handling(
                error_key=FatLink.EsiError.NOT_IN_FLEET, fatlink=fatlink
            )
    else:
        _close_esi_fleet(fatlink=fatlink, reason="No FAT link creator available.")


@shared_task(**{**TASK_DEFAULT_KWARGS, **{"base": QueueOnce}})
def update_esi_fatlinks() -> None:
    """
    Checking ESI fat links for changes

    :return:
    :rtype:
    """

    try:
        esi_fatlinks = FatLink.objects.select_related_default().filter(
            is_esilink=True, is_registered_on_esi=True
        )
    except FatLink.DoesNotExist:
        pass

    # Work our way through the FAT links
    else:
        # Abort if ESI seems to be offline or above the error limit
        if not fetch_esi_status().is_ok:
            logger.warning(
                msg="ESI doesn't seem to be available at this time. Aborting."
            )

            return

        for fatlink in esi_fatlinks:
            _process_esi_fatlink(fatlink=fatlink)


@shared_task
def logrotate():
    """
    Remove logs older than AFAT_DEFAULT_LOG_DURATION

    :return:
    :rtype:
    """

    logger.info(
        msg=f"Cleaning up logs older than {Setting.get_setting(Setting.Field.DEFAULT_LOG_DURATION)} days"
    )

    Log.objects.filter(
        log_time__lte=timezone.now()
        - timedelta(days=Setting.get_setting(Setting.Field.DEFAULT_LOG_DURATION))
    ).delete()
