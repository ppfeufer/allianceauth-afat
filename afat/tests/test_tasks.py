"""
Test cases for the task in the afat module.
"""

# Standard Library
from datetime import timedelta
from unittest.mock import ANY, MagicMock, PropertyMock, patch

# Third Party
import kombu
from bravado.exception import HTTPNotFound

# Django
from django.utils.datetime_safe import datetime

# Alliance Auth AFAT
from afat.models import FatLink
from afat.tasks import (
    _check_for_esi_fleet,
    _close_esi_fleet,
    _esi_fatlinks_error_handling,
    _process_esi_fatlink,
    logrotate,
    process_character,
    process_fats,
    update_esi_fatlinks,
)
from afat.tests import BaseTestCase


class TestLogrotateTask(BaseTestCase):
    """
    Test cases for the logrotate task.
    """

    @patch("afat.tasks.Setting.get_setting")
    @patch("afat.tasks.Log.objects.filter")
    def test_logrotate_removes_old_logs(self, mock_filter, mock_get_setting):
        """
        Test that the logrotate task removes logs older than the specified duration.

        :param mock_filter:
        :type mock_filter:
        :param mock_get_setting:
        :type mock_get_setting:
        :return:
        :rtype:
        """

        mock_get_setting.return_value = 30
        mock_filter.return_value.delete.return_value = None

        logrotate()

        mock_filter.assert_called_once_with(log_time__lte=ANY)
        mock_filter.return_value.delete.assert_called_once()

    @patch("afat.tasks.Setting.get_setting")
    @patch("afat.tasks.Log.objects.filter")
    def test_logrotate_handles_no_old_logs(self, mock_filter, mock_get_setting):
        """
        Test that the logrotate task handles the case where there are no old logs.

        :param mock_filter:
        :type mock_filter:
        :param mock_get_setting:
        :type mock_get_setting:
        :return:
        :rtype:
        """

        mock_get_setting.return_value = 30
        mock_filter.return_value.delete.return_value = None

        logrotate()

        mock_filter.assert_called_once_with(log_time__lte=ANY)
        mock_filter.return_value.delete.assert_called_once()


class TestUpdateEsiFatlinks(BaseTestCase):
    """
    Test cases for the update_esi_fatlinks task.
    """

    @patch("afat.tasks.fetch_esi_status")
    @patch("afat.tasks._process_esi_fatlink")
    @patch("afat.tasks.FatLink.objects.select_related_default")
    def test_updates_esi_fatlinks_when_esi_is_ok(
        self, mock_select_related, mock_process_fatlink, mock_fetch_esi_status
    ):
        """
        Test that the update_esi_fatlinks task updates ESI FAT links when ESI is operational.

        :param mock_select_related:
        :type mock_select_related:
        :param mock_process_fatlink:
        :type mock_process_fatlink:
        :param mock_fetch_esi_status:
        :type mock_fetch_esi_status:
        :return:
        :rtype:
        """

        mock_fatlink1 = MagicMock()
        mock_fatlink2 = MagicMock()

        mock_qs = MagicMock()
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 2
        mock_qs.__iter__.return_value = iter([mock_fatlink1, mock_fatlink2])

        mock_select_related.return_value.filter.return_value.distinct.return_value = (
            mock_qs
        )

        mock_fetch_esi_status.return_value = MagicMock(is_ok=True)

        update_esi_fatlinks()

        mock_process_fatlink.assert_any_call(fatlink=mock_fatlink1)
        mock_process_fatlink.assert_any_call(fatlink=mock_fatlink2)

    @patch("afat.tasks.fetch_esi_status")
    @patch("afat.tasks._process_esi_fatlink")
    @patch("afat.tasks.FatLink.objects.select_related_default")
    def test_aborts_update_when_esi_is_not_ok(
        self, mock_select_related, mock_process_fatlink, mock_fetch_esi_status
    ):
        """
        Test that the update_esi_fatlinks task aborts when ESI is not operational.

        :param mock_select_related:
        :type mock_select_related:
        :param mock_process_fatlink:
        :type mock_process_fatlink:
        :param mock_fetch_esi_status:
        :type mock_fetch_esi_status:
        :return:
        :rtype:
        """

        mock_fatlink1 = MagicMock()
        mock_fatlink2 = MagicMock()

        mock_qs = MagicMock()
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 2
        mock_qs.__iter__.return_value = iter([mock_fatlink1, mock_fatlink2])

        mock_select_related.return_value.filter.return_value.distinct.return_value = (
            mock_qs
        )

        mock_fetch_esi_status.return_value = MagicMock(is_ok=False)

        update_esi_fatlinks()

        mock_process_fatlink.assert_not_called()
        mock_select_related.assert_called_once()

    @patch("afat.tasks.FatLink.objects.select_related_default")
    @patch("afat.tasks.logger")
    def test_logs_message_when_no_esi_fatlinks_to_process(
        self, mock_logger, mock_select_related
    ):
        mock_qs = MagicMock()
        mock_qs.exists.return_value = False
        mock_select_related.return_value.filter.return_value.distinct.return_value = (
            mock_qs
        )

        update_esi_fatlinks()

        mock_logger.debug.assert_called_once_with(msg="No ESI FAT links to process")


class TestProcessEsiFatlink(BaseTestCase):
    """
    Test cases for the _process_esi_fatlink function.
    """

    @patch("afat.utils.esi.__class__.client", new_callable=PropertyMock)
    @patch("afat.tasks._check_for_esi_fleet")
    @patch("afat.tasks._close_esi_fleet")
    @patch("afat.tasks.process_fats.delay")
    def test_processes_fatlink_with_valid_fleet(
        self, mock_process_fats, mock_close_fleet, mock_check_fleet, mock_client_prop
    ):
        """
        Test that the _process_esi_fatlink function processes a FAT link with a valid fleet.

        :param mock_process_fats:
        :type mock_process_fats:
        :param mock_close_fleet:
        :type mock_close_fleet:
        :param mock_check_fleet:
        :type mock_check_fleet:
        :param mock_client_prop:
        :type mock_client_prop:
        :return:
        :rtype:
        """

        mock_fatlink = MagicMock()
        mock_fatlink.hash = "valid_hash"
        mock_fatlink.creator.profile.main_character = True

        mock_esi_fleet = {"fleet": MagicMock(fleet_id=12345), "token": MagicMock()}
        mock_check_fleet.return_value = mock_esi_fleet

        mock_client = MagicMock()
        mock_client.Fleets.GetFleetsFleetIdMembers.return_value.result.return_value = [
            MagicMock(dict=lambda: {"character_id": 1})
        ]
        mock_client_prop.return_value = mock_client

        _process_esi_fatlink(mock_fatlink)

        mock_process_fats.assert_called_once()
        mock_close_fleet.assert_not_called()

    @patch("afat.utils.esi.__class__.client", new_callable=PropertyMock)
    @patch("afat.tasks._check_for_esi_fleet")
    @patch("afat.tasks._close_esi_fleet")
    def test_closes_fatlink_when_no_creator(
        self, mock_close_fleet, mock_check_fleet, mock_client_prop
    ):
        """
        Test that the _process_esi_fatlink function closes a FAT link when there is no creator.

        :param mock_close_fleet:
        :type mock_close_fleet:
        :param mock_check_fleet:
        :type mock_check_fleet:
        :param mock_client_prop:
        :type mock_client_prop:
        :return:
        :rtype:
        """

        mock_fatlink = MagicMock()
        mock_fatlink.hash = "no_creator_hash"
        mock_fatlink.creator.profile.main_character = None

        _process_esi_fatlink(mock_fatlink)

        mock_close_fleet.assert_called_once_with(
            fatlink=mock_fatlink, reason="No FAT link creator available."
        )
        mock_check_fleet.assert_not_called()

    @patch("afat.utils.esi.__class__.client", new_callable=PropertyMock)
    @patch("afat.tasks._check_for_esi_fleet")
    @patch("afat.tasks._esi_fatlinks_error_handling")
    def test_handles_error_when_not_fleetboss(
        self, mock_error_handling, mock_check_fleet, mock_client_prop
    ):
        mock_fatlink = MagicMock()
        mock_fatlink.hash = "not_fleetboss_hash"
        mock_fatlink.creator.profile.main_character = True

        mock_esi_fleet = {"fleet": MagicMock(fleet_id=12345), "token": MagicMock()}
        mock_check_fleet.return_value = mock_esi_fleet

        mock_client = MagicMock()
        mock_client.Fleets.GetFleetsFleetIdMembers.return_value.result.side_effect = (
            Exception
        )
        mock_client_prop.return_value = mock_client

        _process_esi_fatlink(mock_fatlink)

        mock_error_handling.assert_called_once_with(
            error_key=FatLink.EsiError.NOT_FLEETBOSS, fatlink=mock_fatlink
        )

    @patch("afat.utils.esi.__class__.client", new_callable=PropertyMock)
    @patch("afat.tasks._check_for_esi_fleet")
    @patch("afat.tasks._close_esi_fleet")
    def test_skips_processing_when_no_esi_fleet(
        self, mock_close_fleet, mock_check_fleet, mock_client_prop
    ):
        """
        Test that the _process_esi_fatlink function skips processing when there is no ESI fleet.

        :param mock_close_fleet:
        :type mock_close_fleet:
        :param mock_check_fleet:
        :type mock_check_fleet:
        :param mock_client_prop:
        :type mock_client_prop:
        :return:
        :rtype:
        """

        mock_fatlink = MagicMock()
        mock_fatlink.hash = "no_fleet_hash"
        mock_fatlink.creator.profile.main_character = True

        mock_check_fleet.return_value = None

        _process_esi_fatlink(mock_fatlink)

        mock_close_fleet.assert_not_called()


class TestEsiFatlinksErrorHandling(BaseTestCase):
    """
    Test cases for the _esi_fatlinks_error_handling function.
    """

    @patch("afat.tasks.timezone.now")
    @patch("afat.tasks._close_esi_fleet")
    def test_handles_error_within_grace_period(self, mock_close_fleet, mock_now):
        """
        Test that the _esi_fatlinks_error_handling function handles the case when an error occurs within the grace period.

        :param mock_close_fleet:
        :type mock_close_fleet:
        :param mock_now:
        :type mock_now:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        error_key = MagicMock()
        error_key.label = "Test Error"
        now = datetime(2023, 10, 1, 12, 0, 0)
        mock_now.return_value = now
        fatlink.last_esi_error = error_key
        fatlink.last_esi_error_time = now - timedelta(seconds=30)
        fatlink.esi_error_count = 3

        _esi_fatlinks_error_handling(error_key, fatlink)

        mock_close_fleet.assert_called_once_with(
            fatlink=fatlink, reason=error_key.label
        )
        fatlink.save.assert_not_called()

    @patch("afat.tasks.timezone.now")
    def test_increments_error_count(self, mock_now):
        """
        Test that the _esi_fatlinks_error_handling function increments the error count.

        :param mock_now:
        :type mock_now:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        error_key = MagicMock()
        error_key.label = "Test Error"
        now = datetime(2023, 10, 1, 12, 0, 0)
        mock_now.return_value = now
        fatlink.last_esi_error = error_key
        fatlink.last_esi_error_time = now - timedelta(seconds=30)
        fatlink.esi_error_count = 2

        _esi_fatlinks_error_handling(error_key, fatlink)

        self.assertEqual(fatlink.esi_error_count, 3)
        fatlink.save.assert_called_once()

    @patch("afat.tasks.timezone.now")
    def test_resets_error_count_after_grace_period(self, mock_now):
        """
        Test that the _esi_fatlinks_error_handling function resets the error count after the grace period.

        :param mock_now:
        :type mock_now:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        error_key = MagicMock()
        error_key.label = "Test Error"
        now = datetime(2023, 10, 1, 12, 0, 0)
        mock_now.return_value = now
        fatlink.last_esi_error = error_key
        fatlink.last_esi_error_time = now - timedelta(seconds=100)
        fatlink.esi_error_count = 2

        _esi_fatlinks_error_handling(error_key, fatlink)

        self.assertEqual(fatlink.esi_error_count, 1)
        fatlink.save.assert_called_once()

    @patch("afat.tasks.timezone.now")
    def test_handles_new_error(self, mock_now):
        """
        Test that the _esi_fatlinks_error_handling function handles a new error.

        :param mock_now:
        :type mock_now:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        error_key = MagicMock()
        error_key.label = "Test Error"
        now = datetime(2023, 10, 1, 12, 0, 0)
        mock_now.return_value = now
        fatlink.last_esi_error = None
        fatlink.last_esi_error_time = None
        fatlink.esi_error_count = 0

        _esi_fatlinks_error_handling(error_key, fatlink)

        self.assertEqual(fatlink.esi_error_count, 1)
        self.assertEqual(fatlink.last_esi_error, error_key)
        self.assertEqual(fatlink.last_esi_error_time, mock_now.return_value)
        fatlink.save.assert_called_once()


class TestCloseEsiFleet(BaseTestCase):
    """
    Test cases for the _close_esi_fleet function.
    """

    @patch("afat.tasks.logger.info")
    def test_closes_fleet_successfully(self, mock_logger_info):
        """
        Test that the _close_esi_fleet function closes the fleet successfully.

        :param mock_logger_info:
        :type mock_logger_info:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        fatlink.hash = "test_hash"

        _close_esi_fleet(fatlink=fatlink, reason="Test Reason")

        fatlink.is_registered_on_esi = False
        fatlink.save.assert_called_once()
        mock_logger_info.assert_called_once_with(
            msg='Closing ESI FAT link with hash "test_hash". Reason: Test Reason'
        )

    @patch("afat.tasks.logger.info")
    def test_handles_empty_reason(self, mock_logger_info):
        """
        Test that the _close_esi_fleet function handles an empty reason.

        :param mock_logger_info:
        :type mock_logger_info:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        fatlink.hash = "test_hash"

        _close_esi_fleet(fatlink=fatlink, reason="")

        fatlink.is_registered_on_esi = False
        fatlink.save.assert_called_once()
        mock_logger_info.assert_called_once_with(
            msg='Closing ESI FAT link with hash "test_hash". Reason: '
        )

    @patch("afat.tasks.logger.info")
    def test_handles_none_reason(self, mock_logger_info):
        """
        Test that the _close_esi_fleet function handles a None reason.

        :param mock_logger_info:
        :type mock_logger_info:
        :return:
        :rtype:
        """

        fatlink = MagicMock(spec=FatLink)
        fatlink.hash = "test_hash"

        _close_esi_fleet(fatlink=fatlink, reason=None)

        fatlink.is_registered_on_esi = False
        fatlink.save.assert_called_once()
        mock_logger_info.assert_called_once_with(
            msg='Closing ESI FAT link with hash "test_hash". Reason: None'
        )


class TestProcessFats(BaseTestCase):
    """
    Test cases for the process_fats function.
    """

    @patch("afat.tasks.process_character.si")
    @patch("afat.tasks.group")
    def test_processes_fat_link_data_from_esi(
        self, mock_group, mock_process_character_si
    ):
        """
        Test that the process_fats function processes FAT link data from ESI.

        :param mock_group:
        :type mock_group:
        :param mock_process_character_si:
        :type mock_process_character_si:
        :return:
        :rtype:
        """

        data_list = [
            {"character_id": 1, "solar_system_id": 100, "ship_type_id": 200},
            {"character_id": 2, "solar_system_id": 101, "ship_type_id": 201},
        ]
        fatlink_hash = "test_hash"
        mock_group.return_value.delay = MagicMock()

        process_fats(data_list, "esi", fatlink_hash)

        self.assertEqual(mock_process_character_si.call_count, 2)
        mock_group.assert_called_once()
        mock_group.return_value.delay.assert_called_once()

    @patch("afat.tasks.process_character.si")
    @patch("afat.tasks.group")
    def test_processes_fat_link_data_with_no_tasks(
        self, mock_group, mock_process_character_si
    ):
        """
        Test that the process_fats function handles the case when there are no tasks to process.

        :param mock_group:
        :type mock_group:
        :param mock_process_character_si:
        :type mock_process_character_si:
        :return:
        :rtype:
        """

        data_list = []
        fatlink_hash = "test_hash"

        process_fats(data_list, "esi", fatlink_hash)

        mock_process_character_si.assert_not_called()
        mock_group.assert_not_called()

    @patch("afat.tasks.process_character.si")
    @patch("afat.tasks.group")
    def test_handles_kombu_encode_error(self, mock_group, mock_process_character_si):
        data_list = [
            {"character_id": 1, "solar_system_id": 100, "ship_type_id": 200},
        ]
        fatlink_hash = "test_hash"
        mock_group.return_value.delay.side_effect = kombu.exceptions.EncodeError

        process_fats(data_list, "esi", fatlink_hash)

        self.assertEqual(mock_process_character_si.call_count, 1)
        mock_group.assert_called_once()
        mock_group.return_value.delay.assert_called_once()

    @patch("afat.tasks.logger")
    def test_logs_warning_for_unknown_data_source(self, mock_logger):
        """
        Test that the process_fats function logs a warning for an unknown data source.

        :param mock_logger:
        :type mock_logger:
        :return:
        :rtype:
        """

        process_fats(
            data_list=[], data_source="unknown_source", fatlink_hash="test_hash"
        )

        mock_logger.warning.assert_called_once_with(
            msg='Unknown data source "unknown_source" for FAT link hash "test_hash"'
        )

    @patch("afat.tasks.logger")
    def test_does_not_process_for_unknown_data_source(self, mock_logger):
        with patch("afat.tasks.group") as mock_group:
            process_fats(
                data_list=[], data_source="unknown_source", fatlink_hash="test_hash"
            )

            mock_group.assert_not_called()


class TestCheckForEsiFleet(BaseTestCase):
    """
    Test cases for the _check_for_esi_fleet function.
    """

    @patch("afat.utils.esi.__class__.client", new_callable=MagicMock)
    @patch("esi.models.Token.get_token")
    def test_returns_fleet_and_token_when_fleet_is_registered(
        self, mock_get_token, mock_client
    ):
        """
        Test that the _check_for_esi_fleet function returns the fleet and token when the fleet is registered.

        :param mock_get_token:
        :type mock_get_token:
        :param mock_client:
        :type mock_client:
        :return:
        :rtype:
        """

        mock_fatlink = MagicMock()
        mock_fatlink.character.character_id = 12345
        mock_fatlink.esi_fleet_id = 67890

        mock_token = MagicMock()
        mock_get_token.return_value = mock_token

        mock_fleet = MagicMock(fleet_id=67890)
        mock_client.Fleets.GetCharactersCharacterIdFleet.return_value.result.return_value = (
            mock_fleet
        )

        result = _check_for_esi_fleet(fatlink=mock_fatlink)

        self.assertDictEqual(result, {"fleet": mock_fleet, "token": mock_token})

    @patch("afat.tasks._esi_fatlinks_error_handling")
    @patch("afat.utils.esi.__class__.client", new_callable=PropertyMock)
    @patch("esi.models.Token.get_token")
    def test_handles_http_not_found_error_when_checking_esi_fleet(
        self, mock_get_token, mock_client_prop, mock_error_handling
    ):
        mock_fatlink = MagicMock()
        mock_fatlink.character.character_id = 12345
        mock_get_token.return_value = MagicMock()
        mock_client = MagicMock()
        mock_client.Fleets.GetCharactersCharacterIdFleet.return_value.result.side_effect = HTTPNotFound(
            MagicMock()
        )
        mock_client_prop.return_value = mock_client

        result = _check_for_esi_fleet(fatlink=mock_fatlink)

        self.assertIsNone(result)
        mock_error_handling.assert_called_once_with(
            error_key=FatLink.EsiError.NOT_IN_FLEET, fatlink=mock_fatlink
        )

    @patch("afat.utils.esi.__class__.client", new_callable=MagicMock)
    @patch("afat.tasks._esi_fatlinks_error_handling")
    @patch("esi.models.Token.get_token")
    def test_handles_generic_error(
        self, mock_get_token, mock_error_handling, mock_client
    ):
        """
        Test that the _check_for_esi_fleet function handles a generic error.

        :param mock_get_token:
        :type mock_get_token:
        :param mock_error_handling:
        :type mock_error_handling:
        :param mock_client:
        :type mock_client:
        :return:
        :rtype:
        """

        mock_fatlink = MagicMock()
        mock_fatlink.character.character_id = 12345
        mock_fatlink.esi_fleet_id = 67890

        mock_get_token.return_value = MagicMock()
        mock_client.Fleets.GetCharactersCharacterIdFleet.return_value.result.side_effect = (
            Exception
        )

        result = _check_for_esi_fleet(fatlink=mock_fatlink)

        self.assertIsNone(result)
        mock_error_handling.assert_called_once_with(
            error_key=FatLink.EsiError.NO_FLEET, fatlink=mock_fatlink
        )

    @patch("afat.utils.esi.__class__.client", new_callable=MagicMock)
    @patch("afat.tasks._esi_fatlinks_error_handling")
    @patch("esi.models.Token.get_token")
    def test_returns_none_when_fleet_id_does_not_match(
        self, mock_get_token, mock_error_handling, mock_client
    ):
        mock_fatlink = MagicMock()
        mock_fatlink.character.character_id = 12345
        mock_fatlink.esi_fleet_id = 67890

        mock_token = MagicMock()
        mock_get_token.return_value = mock_token

        mock_fleet = MagicMock(fleet_id=11111)
        mock_client.Fleets.GetCharactersCharacterIdFleet.return_value.result.return_value = (
            mock_fleet
        )

        result = _check_for_esi_fleet(fatlink=mock_fatlink)

        self.assertIsNone(result)
        mock_error_handling.assert_called_once_with(
            error_key=FatLink.EsiError.NO_FLEET, fatlink=mock_fatlink
        )


class TestProcessCharacterTask(BaseTestCase):
    """
    Test cases for the process_character task.
    """

    @patch("afat.tasks.logger.info")
    @patch("afat.tasks.logger.debug")
    @patch("afat.utils.esi.__class__.client", new_callable=PropertyMock)
    @patch("afat.tasks.Fat.objects.get_or_create")
    @patch("afat.tasks.FatLink.objects.get")
    @patch("afat.tasks.get_or_create_character")
    def test_processes_character_successfully(
        self,
        mock_get_or_create_character,
        mock_get_fatlink,
        mock_get_or_create_fat,
        mock_client_prop,
        mock_logger_debug,
        mock_logger_info,
    ):
        """
        Test that the process_character task processes a character successfully.

        :param mock_get_or_create_character:
        :type mock_get_or_create_character:
        :param mock_get_fatlink:
        :type mock_get_fatlink:
        :param mock_get_or_create_fat:
        :type mock_get_or_create_fat:
        :param mock_client_prop:
        :type mock_client_prop:
        :param mock_logger_debug:
        :type mock_logger_debug:
        :param mock_logger_info:
        :type mock_logger_info:
        :return:
        :rtype:
        """

        mock_character = MagicMock()
        mock_character.corporation_id = 100
        mock_character.alliance_id = 200
        mock_get_or_create_character.return_value = mock_character

        mock_fatlink = MagicMock()
        mock_get_fatlink.return_value = mock_fatlink

        mock_system = MagicMock()
        mock_system.name = "Test System"

        mock_ship = MagicMock()
        mock_ship.name = "Test Ship"

        mock_client = MagicMock()
        mock_client.Universe.GetUniverseSystemsSystemId.return_value.result.return_value = (
            mock_system
        )
        mock_client.Universe.GetUniverseTypesTypeId.return_value.result.return_value = (
            mock_ship
        )
        mock_client_prop.return_value = mock_client

        mock_fat = MagicMock()
        mock_fat.pk = 1
        mock_get_or_create_fat.return_value = (mock_fat, True)

        process_character(12345, 67890, 111213, "test_hash")

        mock_logger_info.assert_called_once()
        logged_msg = mock_logger_info.call_args[0][0]
        self.assertIn("New Pilot: Adding", logged_msg)
        self.assertIn("in Test System flying a Test Ship", logged_msg)
        self.assertIn('FAT link "test_hash" (FAT ID 1)', logged_msg)

    @patch("afat.tasks.logger.info")
    @patch("afat.tasks.logger.debug")
    @patch("afat.utils.esi.__class__.client", new_callable=PropertyMock)
    @patch("afat.tasks.Fat.objects.get_or_create")
    @patch("afat.tasks.FatLink.objects.get")
    @patch("afat.tasks.get_or_create_character")
    def test_handles_existing_character(
        self,
        mock_get_or_create_character,
        mock_get_fatlink,
        mock_get_or_create_fat,
        mock_client_prop,
        mock_logger_debug,
        mock_logger_info,
    ):
        """
        Test that the process_character task handles an existing character.

        :param mock_get_or_create_character:
        :type mock_get_or_create_character:
        :param mock_get_fatlink:
        :type mock_get_fatlink:
        :param mock_get_or_create_fat:
        :type mock_get_or_create_fat:
        :param mock_client_prop:
        :type mock_client_prop:
        :param mock_logger_debug:
        :type mock_logger_debug:
        :param mock_logger_info:
        :type mock_logger_info:
        :return:
        :rtype:
        """

        mock_character = MagicMock()
        mock_character.corporation_id = 100
        mock_character.alliance_id = 200
        mock_get_or_create_character.return_value = mock_character

        mock_fatlink = MagicMock()
        mock_get_fatlink.return_value = mock_fatlink

        mock_system = MagicMock()
        mock_system.name = "Test System"

        mock_ship = MagicMock()
        mock_ship.name = "Test Ship"

        mock_client = MagicMock()
        mock_client.Universe.GetUniverseSystemsSystemId.return_value.result.return_value = (
            mock_system
        )
        mock_client.Universe.GetUniverseTypesTypeId.return_value.result.return_value = (
            mock_ship
        )
        mock_client_prop.return_value = mock_client

        mock_fat = MagicMock()
        mock_fat.pk = 1
        mock_get_or_create_fat.return_value = (mock_fat, False)

        process_character(12345, 67890, 111213, "test_hash")

        mock_logger_debug.assert_called_once()
        logged_msg = mock_logger_debug.call_args[0][0]
        self.assertIn(
            "already registered for FAT link test_hash with FAT ID 1", logged_msg
        )

    @patch("afat.tasks.logger.warning")
    @patch("afat.utils.esi.__class__.client", new_callable=PropertyMock)
    @patch("afat.tasks.Fat.objects.get_or_create")
    @patch("afat.tasks.FatLink.objects.get")
    @patch("afat.tasks.get_or_create_character")
    def test_handles_missing_fatlink(
        self,
        mock_get_or_create_character,
        mock_get_fatlink,
        mock_get_or_create_fat,
        mock_client_prop,
        mock_logger_warning,
    ):
        mock_get_fatlink.side_effect = FatLink.DoesNotExist

        # Ensure client is patched to avoid network calls during patch setup
        mock_client_prop.return_value = MagicMock()

        process_character(12345, 67890, 111213, "test_hash")

        mock_logger_warning.assert_called_once()
        logged_msg = mock_logger_warning.call_args[0][0]
        self.assertIn("FAT link with hash", logged_msg)
        self.assertIn('"test_hash"', logged_msg)
        self.assertIn("skipping character 12345", logged_msg)

    @patch("afat.tasks.logger.info")
    @patch("afat.utils.esi.__class__.client", new_callable=PropertyMock)
    @patch("afat.tasks.Fat.objects.get_or_create")
    @patch("afat.tasks.FatLink.objects.get")
    @patch("afat.tasks.get_or_create_character")
    def handles_esi_client_error(
        self,
        mock_get_or_create_character,
        mock_get_fatlink,
        mock_get_or_create_fat,
        mock_client_prop,
        mock_logger_info,
    ):
        mock_client = MagicMock()
        mock_client.Universe.GetUniverseSystemsSystemId.return_value.result.side_effect = Exception(
            "ESI client error"
        )
        mock_client_prop.return_value = mock_client

        process_character(12345, 67890, 111213, "test_hash")

        mock_logger_info.assert_called_once_with(
            "Error occurred while processing character 12345 for FAT link test_hash: ESI client error"
        )
