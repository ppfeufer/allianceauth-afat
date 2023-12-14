"""
The models
"""

# Django
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth AFAT
from afat.managers import FatLinkManager, FatManager


def get_sentinel_user() -> User:
    """
    Get user or create the sentinel user

    :return:
    """

    return User.objects.get_or_create(username="deleted")[0]


def get_hash_on_save() -> str:
    """
    Get the hash

    :return:
    """

    fatlink_hash = get_random_string(length=30)

    while FatLink.objects.filter(hash=fatlink_hash).exists():
        fatlink_hash = get_random_string(length=30)

    return fatlink_hash


class General(models.Model):
    """
    Meta model for app permissions
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        AaAfat :: Meta
        """

        managed = False
        default_permissions = ()
        permissions = (
            # can access and register his own participation to a FAT link
            ("basic_access", _("Can access the AFAT module")),
            # Can manage the FAT module
            # Has:
            #   » add_fatlink
            #   » change_fatlink
            #   » delete_fatlink
            #   » add_fat
            #   » delete_fat
            ("manage_afat", _("Can manage the AFAT module")),
            # Can add a new FAT link
            ("add_fatlink", _("Can create FAT links")),
            # Can see own corp stats
            ("stats_corporation_own", _("Can see own corporation statistics")),
            # Can see the stats of all corps
            ("stats_corporation_other", _("Can see statistics of other corporations")),
            # Can view the modules log
            ("log_view", _("Can view the modules log")),
        )
        verbose_name = _("AFAT")


class FleetType(models.Model):
    """
    FAT link fleet type

    Example:
        - CTA
        - Home Defense
        - StratOP
        - and so on …
    """

    id = models.AutoField(primary_key=True)

    name = models.CharField(
        max_length=254, help_text=_("Descriptive name of the fleet type")
    )

    is_enabled = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Whether this fleet type is active or not"),
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Fleet type")
        verbose_name_plural = _("Fleet types")

    def __str__(self) -> str:
        """
        Return the objects string name

        :return:
        :rtype:
        """

        return str(self.name)


class FatLink(models.Model):
    """
    FAT link
    """

    class EsiError(models.TextChoices):
        """
        Choices for SRP Status
        """

        NOT_IN_FLEET = "NOT_IN_FLEET", _(
            "FC is not in the registered fleet anymore or fleet is no longer available."
        )
        NO_FLEET = "NO_FLEET", _("Registered fleet seems to be no longer available.")
        NOT_FLEETBOSS = "NOT_FLEETBOSS", _("FC is no longer the fleet boss.")

    created = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text=_("When was this FAT link created"),
    )

    fleet = models.CharField(
        max_length=254,
        blank=False,
        default=None,
        help_text=_("The FAT link fleet name"),
    )

    hash = models.CharField(
        max_length=254, db_index=True, unique=True, help_text=_("The FAT link hash")
    )

    creator = models.ForeignKey(
        to=User,
        related_name="+",
        on_delete=models.SET(get_sentinel_user),
        help_text=_("Who created the FAT link?"),
    )

    character = models.ForeignKey(
        to=EveCharacter,
        related_name="+",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        help_text=_("Character this FAT link has been created with"),
    )

    link_type = models.ForeignKey(
        to=FleetType,
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
        help_text=_("The FAT link fleet type, if it's set"),
    )

    is_esilink = models.BooleanField(
        default=False, help_text=_("Whether this FAT link was created via ESI or not")
    )

    is_registered_on_esi = models.BooleanField(
        default=False,
        help_text=_("Whether the fleet to this FAT link is available in ESI or not"),
    )

    esi_fleet_id = models.BigIntegerField(blank=True, null=True)

    reopened = models.BooleanField(
        default=False, help_text=_("Has this FAT link being re-opened?")
    )

    last_esi_error = models.CharField(
        max_length=15, blank=True, default="", choices=EsiError.choices
    )

    last_esi_error_time = models.DateTimeField(null=True, blank=True, default=None)

    esi_error_count = models.IntegerField(default=0)

    objects = FatLinkManager()

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        default_permissions = ()
        ordering = ("-created",)
        verbose_name = _("FAT link")
        verbose_name_plural = _("FAT links")

    def __str__(self) -> str:
        """
        Return the objects string name

        :return:
        :rtype:
        """

        return f"{self.fleet} - {self.hash}"

    @transaction.atomic()
    def save(self, *args, **kwargs):
        """
        Add the hash on save

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        try:
            self.hash
        except ObjectDoesNotExist:
            self.hash = get_hash_on_save()
        super().save(*args, **kwargs)

    @property
    def number_of_fats(self):
        """
        Returns the number of registered FATs

        :return:
        :rtype:
        """

        return self.afat_fats.count()


class Duration(models.Model):
    """
    FAT link duration (expiry time in minutes)
    """

    duration = models.PositiveIntegerField()
    fleet = models.ForeignKey(
        to=FatLink, related_name="duration", on_delete=models.CASCADE
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("FAT link duration")
        verbose_name_plural = _("FAT link durations")


# AFat Model
class Fat(models.Model):
    """
    AFat
    """

    character = models.ForeignKey(
        to=EveCharacter,
        related_name="afat_fats",
        on_delete=models.CASCADE,
        help_text=_("Character who registered this FAT"),
    )

    fatlink = models.ForeignKey(
        to=FatLink,
        related_name="afat_fats",
        on_delete=models.CASCADE,
        help_text=_("The FAT link the character registered at"),
    )

    system = models.CharField(
        max_length=100, null=True, help_text=_("The system the character is in")
    )

    shiptype = models.CharField(
        max_length=100,
        null=True,
        db_index=True,
        help_text=_("The ship the character was flying"),
    )

    objects = FatManager()

    class Meta:  # pylint: disable=too-few-public-methods
        """
        AFat :: Meta
        """

        default_permissions = ()
        unique_together = (("character", "fatlink"),)
        verbose_name = _("FAT")
        verbose_name_plural = _("FATs")

    def __str__(self) -> str:
        """
        Return the objects string name

        :return:
        :rtype:
        """

        return f"{self.fatlink} - {self.character}"


# AFat Log Model
class Log(models.Model):
    """
    The log
    """

    class Event(models.TextChoices):
        """
        Choices for SRP Status
        """

        CREATE_FATLINK = "CR_FAT_LINK", _("FAT link created")
        CHANGE_FATLINK = "CH_FAT_LINK", _("FAT link changed")
        DELETE_FATLINK = "RM_FAT_LINK", _("FAT link removed")
        REOPEN_FATLINK = "RO_FAT_LINK", _("FAT link re-opened")
        # CREATE_FAT = "CR_FAT", _("FAT registered")
        DELETE_FAT = "RM_FAT", _("FAT removed")
        MANUAL_FAT = "CR_FAT_MAN", _("Manual FAT added")

    log_time = models.DateTimeField(default=timezone.now, db_index=True)
    user = models.ForeignKey(
        to=User,
        related_name="afat_log",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET(value=get_sentinel_user),
    )
    log_event = models.CharField(
        max_length=11,
        blank=False,
        choices=Event.choices,
        default=Event.CREATE_FATLINK,
    )
    log_text = models.TextField()
    fatlink_hash = models.CharField(max_length=254)

    class Meta:  # pylint: disable=too-few-public-methods
        """
        AFatLog :: Meta
        """

        default_permissions = ()
        verbose_name = _("Log")
        verbose_name_plural = _("Logs")
