# Standard Library
from unittest.mock import MagicMock, PropertyMock, patch

# Alliance Auth
from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)

# Alliance Auth AFAT
from afat.tests import BaseTestCase
from afat.utils import (
    NoDataError,
    get_main_character_from_user,
    get_or_create_alliance_info,
    get_or_create_character,
    get_or_create_corporation_info,
)


class TestGetMainCharacterFromUser(BaseTestCase):
    """
    Test the get_main_character_from_user function
    """

    def test_returns_main_character_name_when_user_has_profile(self):
        """
        Test that the function returns the main character name when the user has a profile

        :return:
        :rtype:
        """

        mock_user = MagicMock()
        mock_user.username = "test_user"
        mock_user.profile.main_character.character_name = "Main Character"

        result = get_main_character_from_user(mock_user)

        self.assertEqual(result, "Main Character")

    def test_returns_username_when_user_has_no_profile(self):
        """
        Test that the function returns the username when the user has no profile

        :return:
        :rtype:
        """

        mock_user = MagicMock()
        mock_user.username = "test_user"
        mock_user.profile = None

        result = get_main_character_from_user(mock_user)

        self.assertEqual(result, "test_user")

    def test_returns_username_when_profile_has_no_main_character(self):
        """
        Test that the function returns the username when the profile has no main character

        :return:
        :rtype:
        """

        mock_user = MagicMock()
        mock_user.username = "test_user"
        mock_user.profile.main_character = None

        result = get_main_character_from_user(mock_user)

        self.assertEqual(result, "test_user")


class TestGetOrCreateAllianceInfo(BaseTestCase):
    """
    Test the get_or_create_alliance_info function
    """

    @patch("allianceauth.eveonline.models.EveAllianceInfo.objects.create_alliance")
    def test_returns_existing_alliance_info(self, mock_create_alliance):
        """
        Test that the function returns existing alliance info

        :param mock_create_alliance:
        :type mock_create_alliance:
        :return:
        :rtype:
        """

        mock_alliance = EveAllianceInfo(
            alliance_id=12345, alliance_name="Existing Alliance"
        )
        mock_create_alliance.return_value = mock_alliance

        result = get_or_create_alliance_info(alliance_id=12345)

        self.assertEqual(result, mock_alliance)

    @patch("afat.utils.logger.info")
    @patch("allianceauth.eveonline.models.EveAllianceInfo.objects.create_alliance")
    def test_creates_new_alliance_info_when_not_found(
        self, mock_create_alliance, mock_logger
    ):
        """
        Test that the function creates new alliance info when not found

        :param mock_create_alliance:
        :type mock_create_alliance:
        :param mock_logger:
        :type mock_logger:
        :return:
        :rtype:
        """

        mock_create_alliance.return_value = EveAllianceInfo(
            alliance_id=67890, alliance_name="Test Alliance"
        )

        result = get_or_create_alliance_info(alliance_id=67890)

        self.assertEqual(result.alliance_id, 67890)
        self.assertEqual(result.alliance_name, "Test Alliance")
        mock_logger.assert_called_once_with(
            msg="EveAllianceInfo object created: Test Alliance"
        )


class TestGetOrCreateCorporationInfo(BaseTestCase):
    """
    Test the get_or_create_corporation_info function
    """

    @patch(
        "allianceauth.eveonline.models.EveCorporationInfo.objects.create_corporation"
    )
    def test_returns_existing_corporation_info(self, mock_create_corporation):
        """
        Test that the function returns existing corporation info

        :param mock_create_corporation:
        :type mock_create_corporation:
        :return:
        :rtype:
        """

        mock_corporation = MagicMock()
        mock_corporation.corporation_id = 12345
        mock_corporation.corporation_name = "Existing Corporation"
        with patch(
            "allianceauth.eveonline.models.EveCorporationInfo.objects.get",
            return_value=mock_corporation,
        ):
            result = get_or_create_corporation_info(corporation_id=12345)

            self.assertEqual(result, mock_corporation)
            mock_create_corporation.assert_not_called()

    @patch("afat.utils.logger.info")
    @patch(
        "allianceauth.eveonline.models.EveCorporationInfo.objects.create_corporation"
    )
    def test_creates_new_corporation_info_when_not_found(
        self, mock_create_corporation, mock_logger
    ):
        """
        Test that the function creates new corporation info when not found

        :param mock_create_corporation:
        :type mock_create_corporation:
        :param mock_logger:
        :type mock_logger:
        :return:
        :rtype:
        """

        mock_create_corporation.return_value = MagicMock(
            corporation_id=67890, corporation_name="Test Corporation"
        )

        with patch(
            "allianceauth.eveonline.models.EveCorporationInfo.objects.get",
            side_effect=EveCorporationInfo.DoesNotExist,
        ):
            result = get_or_create_corporation_info(corporation_id=67890)

            self.assertEqual(result.corporation_id, 67890)
            self.assertEqual(result.corporation_name, "Test Corporation")
            mock_logger.assert_called_once_with(
                msg="EveCorporationInfo object created: Test Corporation"
            )


def get_or_create_character_info(character_id):
    pass


class EveCharacterInfo:
    pass


class TestGetOrCreateCharacterInfo(BaseTestCase):
    """
    Test the get_or_create_character_info function
    """

    @patch("afat.utils.esi.__class__.client", new_callable=PropertyMock)
    @patch("allianceauth.eveonline.models.EveCharacter.objects.filter")
    def test_returns_existing_character_by_name(self, mock_filter, mock_client_prop):
        """
        Test that the function returns existing character by name

        :param mock_filter:
        :type mock_filter:
        :param mock_client_prop:
        :type mock_client_prop:
        :return:
        :rtype:
        """

        mock_universe = MagicMock()
        mock_universe.PostUniverseIds.return_value.results.return_value = {
            "characters": [{"id": 12345}]
        }
        mock_client_prop.return_value = MagicMock(Universe=mock_universe)
        mock_character = EveCharacter(
            character_id=12345, character_name="Test Character"
        )
        mock_filter.return_value = [mock_character]

        result = get_or_create_character(name="Test Character")

        self.assertEqual(result, mock_character)

    @patch("allianceauth.eveonline.models.EveCharacter.objects.filter")
    def test_returns_existing_character_by_id(self, mock_filter):
        """
        Test that the function returns existing character by ID

        :param mock_filter:
        :type mock_filter:
        :return:
        :rtype:
        """

        mock_character = EveCharacter(
            character_id=12345, character_name="Test Character"
        )
        mock_filter.return_value = [mock_character]

        result = get_or_create_character(character_id=12345)

        self.assertEqual(result, mock_character)

    @patch("afat.utils.esi.__class__.client", new_callable=PropertyMock)
    def test_returns_none_when_character_not_found_by_name(self, mock_client_prop):
        """
        Test that the function returns None when character not found by name

        :param mock_client_prop:
        :type mock_client_prop:
        :return:
        :rtype:
        """

        mock_universe = MagicMock()
        mock_universe.PostUniverseIds.return_value.results.return_value = {
            "characters": None
        }
        mock_client_prop.return_value = MagicMock(Universe=mock_universe)

        result = get_or_create_character(name="Nonexistent Character")

        self.assertIsNone(result)

    def test_raises_error_when_no_name_or_id_provided(self):
        """
        Test that the function raises NoDataError when no name or ID is provided

        :return:
        :rtype:
        """

        with self.assertRaises(NoDataError):
            get_or_create_character()

    @patch("afat.utils.esi.__class__.client", new_callable=PropertyMock)
    @patch("allianceauth.eveonline.models.EveCharacter.objects.create_character")
    @patch("allianceauth.eveonline.models.EveCharacter.objects.get")
    @patch("allianceauth.eveonline.models.EveCharacter.objects.filter")
    def test_creates_new_character_and_related_objects(
        self,
        mock_filter,
        mock_get,
        mock_create_character,
        mock_client_prop,
    ):
        mock_universe = MagicMock()
        mock_universe.PostUniverseIds.return_value.results.return_value = {
            "characters": [{"id": 12345}]
        }
        mock_client_prop.return_value = MagicMock(Universe=mock_universe)
        mock_filter.return_value = []
        mock_character = EveCharacter(
            character_id=12345, character_name="New Character", alliance_id=67890
        )
        mock_create_character.return_value = mock_character
        mock_get.return_value = mock_character

        with (
            patch(
                "allianceauth.eveonline.models.EveAllianceInfo.objects.filter"
            ) as mock_alliance_filter,
            patch(
                "allianceauth.eveonline.models.EveAllianceInfo.objects.create_alliance"
            ) as mock_create_alliance,
        ):
            mock_alliance_filter.return_value.exists.return_value = False
            mock_create_alliance.return_value = EveAllianceInfo(alliance_id=67890)

            result = get_or_create_character(name="New Character")
            self.assertEqual(result, mock_character)
            mock_create_alliance.assert_called_once_with(alliance_id=67890)
