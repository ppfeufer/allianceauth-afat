# Standard Library
import datetime as dt
from http import HTTPStatus
from unittest.mock import MagicMock, patch

# Third Party
from eve_sde.models import ItemType

# Django
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth AFAT
from afat.models import Fat, FatLink
from afat.tests import BaseTestCase
from afat.tests.fixtures.utils import (
    RequestStub,
    add_character_to_user,
    create_user_from_evecharacter,
)
from afat.views import statistics as statistics_module
from afat.views.statistics import _calculate_year_stats

MODULE_PATH = "afat.views.statistics"


def response_content_to_str(response) -> str:
    """
    Convert response content to string

    :param response:
    :type response:
    :return:
    :rtype:
    """

    return response.content.decode(response.charset)


class TestStatistics(BaseTestCase):
    """
    Test the statistics views
    """

    @classmethod
    def setUpClass(cls):
        """
        Setup the test class

        :return:
        :rtype:
        """

        super().setUpClass()

        cls.character_1001 = EveCharacter.objects.get(character_id=1001)
        cls.character_1002 = EveCharacter.objects.get(character_id=1002)
        cls.character_1003 = EveCharacter.objects.get(character_id=1003)
        cls.character_1004 = EveCharacter.objects.get(character_id=1004)
        cls.character_1005 = EveCharacter.objects.get(character_id=1005)
        cls.character_1101 = EveCharacter.objects.get(character_id=1101)

        cls.user_without_access, _ = create_user_from_evecharacter(
            character_id=cls.character_1001.character_id
        )

        cls.user_with_basic_access, _ = create_user_from_evecharacter(
            character_id=cls.character_1002.character_id,
            permissions=["afat.basic_access"],
        )

        add_character_to_user(
            user=cls.user_with_basic_access, character=cls.character_1101
        )

        cls.user_with_manage_afat, _ = create_user_from_evecharacter(
            character_id=cls.character_1003.character_id,
            permissions=["afat.basic_access", "afat.manage_afat"],
        )

        cls.user_with_stats_corporation_other, _ = create_user_from_evecharacter(
            character_id=cls.character_1004.character_id,
            permissions=["afat.basic_access", "afat.stats_corporation_other"],
        )

        cls.user_with_stats_corporation_own, _ = create_user_from_evecharacter(
            character_id=cls.character_1005.character_id,
            permissions=["afat.basic_access", "afat.stats_corporation_own"],
        )

        # Generate some FAT links and FATs
        afat_link_april_1 = FatLink.objects.create(
            fleet="April Fleet 1",
            hash="1231",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            created=dt.datetime(year=2020, month=4, day=1, tzinfo=dt.timezone.utc),
        )
        afat_link_april_2 = FatLink.objects.create(
            fleet="April Fleet 2",
            hash="1232",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            created=dt.datetime(year=2020, month=4, day=15, tzinfo=dt.timezone.utc),
        )
        afat_link_september = FatLink.objects.create(
            fleet="September Fleet",
            hash="1233",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            created=dt.datetime(year=2020, month=9, day=1, tzinfo=dt.timezone.utc),
        )
        # Ensure SDE ItemType instances exist and assign them to the Fat.ship FK
        omen = ItemType.objects.get_or_create(
            id=7001, defaults={"name": "Omen", "published": 1}
        )[0]
        thorax = ItemType.objects.get_or_create(
            id=7002, defaults={"name": "Thorax", "published": 1}
        )[0]
        guardian = ItemType.objects.get_or_create(
            id=7003, defaults={"name": "Guardian", "published": 1}
        )[0]

        Fat.objects.create(
            character=cls.character_1101,
            fatlink=afat_link_april_1,
            shiptype="Omen",
            ship=omen,
        )
        Fat.objects.create(
            character=cls.character_1001,
            fatlink=afat_link_april_1,
            shiptype="Omen",
            ship=omen,
        )
        Fat.objects.create(
            character=cls.character_1002,
            fatlink=afat_link_april_1,
            shiptype="Omen",
            ship=omen,
        )
        Fat.objects.create(
            character=cls.character_1003,
            fatlink=afat_link_april_1,
            shiptype="Omen",
            ship=omen,
            corporation_eve_id=2002,
            alliance_eve_id=3001,
        )
        Fat.objects.create(
            character=cls.character_1004,
            fatlink=afat_link_april_1,
            shiptype="Omen",
            ship=omen,
        )
        Fat.objects.create(
            character=cls.character_1005,
            fatlink=afat_link_april_1,
            shiptype="Omen",
            ship=omen,
        )

        Fat.objects.create(
            character=cls.character_1101,
            fatlink=afat_link_april_2,
            shiptype="Omen",
            ship=omen,
        )
        Fat.objects.create(
            character=cls.character_1004,
            fatlink=afat_link_april_2,
            shiptype="Thorax",
            ship=thorax,
        )
        Fat.objects.create(
            character=cls.character_1002,
            fatlink=afat_link_april_2,
            shiptype="Thorax",
            ship=thorax,
        )
        Fat.objects.create(
            character=cls.character_1003,
            fatlink=afat_link_april_2,
            shiptype="Omen",
            ship=omen,
            corporation_eve_id=2002,
            alliance_eve_id=3001,
        )

        Fat.objects.create(
            character=cls.character_1001,
            fatlink=afat_link_september,
            shiptype="Omen",
            ship=omen,
        )
        Fat.objects.create(
            character=cls.character_1004,
            fatlink=afat_link_september,
            shiptype="Guardian",
            ship=guardian,
        )
        Fat.objects.create(
            character=cls.character_1005,
            fatlink=afat_link_september,
            shiptype="Omen",
            ship=omen,
        )

    def test_should_only_show_my_chars_and_only_those_with_fat_links(self):
        """
        Test that the overview page only shows the characters of the user that have FAT links.

        :return:
        :rtype:
        """

        result = _calculate_year_stats(
            request=RequestStub(user=self.user_with_basic_access), year=2020
        )

        self.assertDictEqual(
            d1=result,
            d2={
                "total": {4: 4},
                "characters": [
                    ("Clark Kent", {4: 2}, 1002),
                    ("Lex Luther", {4: 2}, 1101),
                ],
            },
        )

    def test_should_show_statistics_dashboard(self):
        """
        Test should show statistics dashboard

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_basic_access)

        url = reverse(viewname="afat:statistics_overview")
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_statistics_dashboard_for_year(self):
        """
        Test should show statistics dashboard for year

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_basic_access)

        url = reverse(viewname="afat:statistics_overview", kwargs={"year": 2020})
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_statistics_dashboard_for_user_with_stats_corporation_other(
        self,
    ):
        """
        Test should show statistics dashboard for user with stats_corporation_other

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_stats_corporation_other)

        url = reverse(viewname="afat:statistics_overview")
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_statistics_dashboard_for_user_with_stats_corporation_own(self):
        """
        Test should show statistics dashboard for user with stats_corporation_own

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_stats_corporation_own)

        url = reverse(viewname="afat:statistics_overview")
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_not_show_statistics_dashboard_for_user_without_access(self):
        """
        Test should not show statistics dashboard for user without access

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_without_access)

        url = reverse(viewname="afat:statistics_overview")
        res = self.client.get(path=url)

        self.assertNotEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(
            first=res.url,
            second="/account/login/?next=/fleet-activity-tracking/statistics/",
        )

    def test_should_show_own_character_stats(self):
        """
        Test should show own character stats

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_basic_access)

        url = reverse(
            viewname="afat:statistics_character",
            kwargs={
                "charid": self.user_with_basic_access.profile.main_character.character_id,
                "year": 2020,
                "month": 4,
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_other_character_stats_for_user_with_stats_corporation_own(
        self,
    ):
        """
        Test should show other character stats for user with stats_corporation_own

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_stats_corporation_own)

        url = reverse(
            viewname="afat:statistics_character",
            kwargs={
                "charid": self.user_with_basic_access.profile.main_character.character_id,
                "year": 2020,
                "month": 4,
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_other_character_stats_for_user_with_stats_corporation_other(
        self,
    ):
        """
        Test should show other character stats for user with stats_corporation_other

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_stats_corporation_other)

        url = reverse(
            viewname="afat:statistics_character",
            kwargs={
                "charid": self.user_with_basic_access.profile.main_character.character_id,
                "year": 2020,
                "month": 4,
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_other_character_stats_for_user_with_manage_afat(self):
        """
        Test should show other character stats for user with manage_afat

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_manage_afat)

        url = reverse(
            viewname="afat:statistics_character",
            kwargs={
                "charid": self.user_with_basic_access.profile.main_character.character_id,
                "year": 2020,
                "month": 4,
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_not_show_other_character_stats_for_user(self):
        """
        Test should not show other character stats for user without access

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_basic_access)

        url = reverse(
            viewname="afat:statistics_character",
            kwargs={
                "charid": self.user_with_stats_corporation_other.profile.main_character.character_id,
                "year": 2020,
                "month": 4,
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_should_show_own_corp_stats_for_user_with_stats_corporation_own(self):
        """
        Test should show own corp stats for user with stats_corporation_own

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_stats_corporation_own)

        url = reverse(
            viewname="afat:statistics_corporation",
            kwargs={
                "corpid": self.user_with_stats_corporation_own.profile.main_character.corporation_id
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_other_corp_stats_for_user_with_stats_corporation_other(self):
        """
        Test should show other corp stats for user with stats_corporation_other

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_stats_corporation_other)

        url = reverse(
            viewname="afat:statistics_corporation",
            kwargs={
                "corpid": self.user_with_basic_access.profile.main_character.corporation_id
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_other_corp_stats_for_user_with_manage_afat(self):
        """
        Test should show other corp stats for user with manage_afat

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_manage_afat)

        url = reverse(
            viewname="afat:statistics_corporation",
            kwargs={
                "corpid": self.user_with_basic_access.profile.main_character.corporation_id
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_not_show_own_corp_stats_for_user(self):
        """
        Test should not show own corp stats for user without access

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_basic_access)

        url = reverse(
            viewname="afat:statistics_corporation",
            kwargs={
                "corpid": self.user_with_basic_access.profile.main_character.corporation_id
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_should_not_show_other_corp_stats_for_user(self):
        """
        Test should not show other corp stats for user without access

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_basic_access)

        url = reverse(
            viewname="afat:statistics_corporation",
            kwargs={
                "corpid": self.user_with_stats_corporation_other.profile.main_character.corporation_id
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_should_show_all_corp_stats_for_user_with_stats_corporation_other(self):
        """
        Test should show all corp stats for user with stats_corporation_other

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_stats_corporation_other)

        url = reverse(
            viewname="afat:statistics_corporation",
            kwargs={"corpid": 2002, "year": 2020},
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_all_corp_stats_with_month_for_user_with_stats_corporation_other(
        self,
    ):
        """
        Test should show all corp stats with month for user with stats_corporation_other

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_stats_corporation_other)

        url = reverse(
            viewname="afat:statistics_corporation",
            kwargs={"corpid": 2002, "year": 2020, "month": 4},
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

        data_stacked = res.context["data_stacked"]
        character_names = data_stacked[0]
        ship_counts = {
            ship_name: counts[0] for ship_name, _color, counts in data_stacked[1]
        }

        self.assertEqual(first=character_names, second=["Peter Parker"])
        self.assertEqual(first=ship_counts, second={"Omen": 2})

    def test_should_not_show_all_corp_stats_for_user_with_stats_corporation_own(self):
        """
        Test should not show all corp stats for user with stats_corporation_own

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_stats_corporation_own)

        url = reverse(viewname="afat:statistics_corporation", kwargs={"corpid": 2002})
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(first=res.url, second="/fleet-activity-tracking/")

    def test_should_show_all_alliance_stats_with_for_user_with_stats_corporation_other(
        self,
    ):
        """
        Test should show all alliance stats for user with stats_corporation_other

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_stats_corporation_other)

        url = reverse(
            viewname="afat:statistics_alliance",
            kwargs={"allianceid": 3001},
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_all_alliance_stats_with_for_user_with_manage_afat(
        self,
    ):
        """
        Test should show all alliance stats for user with manage_afat

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_manage_afat)

        url = reverse(
            viewname="afat:statistics_alliance",
            kwargs={"allianceid": 3001},
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_all_alliance_stats_with_year_for_user_with_stats_corporation_other(
        self,
    ):
        """
        Test should show all alliance stats with year for user with stats_corporation_other

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_stats_corporation_other)

        url = reverse(
            viewname="afat:statistics_alliance",
            kwargs={"allianceid": 3001, "year": 2020},
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_all_alliance_stats_with_year_for_user_with_manage_afat(
        self,
    ):
        """
        Test should show all alliance stats with year for user with manage_afat

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_manage_afat)

        url = reverse(
            viewname="afat:statistics_alliance",
            kwargs={"allianceid": 3001, "year": 2020},
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_all_alliance_stats_with_month_for_user_with_stats_corporation_other(
        self,
    ):
        # given
        self.client.force_login(user=self.user_with_stats_corporation_other)

        # when
        url = reverse(
            viewname="afat:statistics_alliance",
            kwargs={"allianceid": 3001, "year": 2020, "month": 4},
        )
        res = self.client.get(path=url)

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_all_alliance_stats_with_month_for_user_with_manage_afat(
        self,
    ):
        """
        Test should show all alliance stats with month for user with manage_afat

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_manage_afat)

        url = reverse(
            viewname="afat:statistics_alliance",
            kwargs={"allianceid": 3001, "year": 2020, "month": 4},
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_not_show_all_alliance_stats_for_user(
        self,
    ):
        """
        Test should not show all alliance stats for user without access

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_basic_access)

        url = reverse(
            viewname="afat:statistics_alliance",
            kwargs={"allianceid": 3001},
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_should_show_main_details_for_user_with_manage_perms(self):
        """
        Test that a user with the required permissions can access the view

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_manage_afat)

        url = reverse(
            viewname="afat:statistics_ajax_get_monthly_fats_for_main_character",
            kwargs={
                "corporation_id": self.user_with_basic_access.profile.main_character.corporation_id,
                "character_id": self.user_with_basic_access.profile.main_character.character_id,
                "year": 2020,
                "month": 4,
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_main_details_for_user_with_corporation_other_perms(self):
        """
        Test that a user with the required permissions can access the view (corporation_other)

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_stats_corporation_other)

        url = reverse(
            viewname="afat:statistics_ajax_get_monthly_fats_for_main_character",
            kwargs={
                "corporation_id": self.user_with_basic_access.profile.main_character.corporation_id,
                "character_id": self.user_with_basic_access.profile.main_character.character_id,
                "year": 2020,
                "month": 4,
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_not_show_main_details_for_user_without_perms(self):
        """
        Test that a user without the required permissions cannot access the view

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_with_basic_access)

        url = reverse(
            viewname="afat:statistics_ajax_get_monthly_fats_for_main_character",
            kwargs={
                "corporation_id": self.user_with_basic_access.profile.main_character.corporation_id,
                "character_id": self.user_with_basic_access.profile.main_character.character_id,
                "year": 2020,
                "month": 4,
            },
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(
            first=response_content_to_str(response=res),
            second="",
        )

    @patch("afat.views.statistics.user_has_any_perms", return_value=False)
    @patch("afat.views.statistics.EveCharacter.objects.get")
    def test_should_return_empty_json_when_corporation_differs_and_user_lacks_perms(
        self, mock_get_character, _mock_user_has_any_perms
    ):
        """
        Test that the view returns an empty JSON response when the requester is from
        another corporation and has no permission to view other corps.

        :return:
        :rtype:
        """

        request = RequestFactory().get(path="/dummy")
        request.user = self.user_with_basic_access

        mock_get_character.return_value = MagicMock(corporation_id=999999)

        response = statistics_module.ajax_get_monthly_fats_for_main_character.__wrapped__.__wrapped__(
            request=request,
            corporation_id=999999,
            character_id=123456,
            year=2020,
            month=4,
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
        self.assertEqual(first=response_content_to_str(response=response), second='""')

    @patch("afat.views.statistics.render")
    @patch("afat.views.statistics.Fat.objects.filter")
    @patch("afat.views.statistics.get_or_create_corporation_info")
    def test_should_set_month_average_to_zero_when_corporation_has_no_members(
        self, mock_get_corp, mock_fat_filter, mock_render
    ):
        """
        Test that the view sets the month average to zero when the corporation has no members.

        :param mock_get_corp:
        :param mock_fat_filter:
        :param mock_render:
        :return:
        """

        mock_get_corp.return_value = MagicMock(
            corporation_name="Zero Member Corp", member_count=0
        )

        mock_values = MagicMock()
        mock_values.annotate.return_value = [
            {"fatlink__created__month": 4, "fat_count": 3}
        ]
        mock_fat_filter.return_value.values.return_value = mock_values

        mock_render.return_value = HttpResponse("ok")

        self.client.force_login(user=self.user_with_stats_corporation_other)

        response = self.client.get(
            path=reverse(
                viewname="afat:statistics_corporation",
                kwargs={"corpid": 999999, "year": 2020},
            )
        )

        context = mock_render.call_args.kwargs["context"]

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
        self.assertEqual(first=context["months"], second=[(4, 3, 0)])

    @patch(
        "afat.views.statistics.get_main_character_from_evecharacter", return_value=None
    )
    def test_should_not_add_main_character_when_main_character_is_missing(
        self, _mock_get_main_character
    ):
        """
        Test that the view does not add a main character to the context when the main character is missing.

        :param _mock_get_main_character:
        :return:
        """

        self.client.force_login(user=self.user_with_stats_corporation_other)

        url = reverse(
            viewname="afat:statistics_corporation",
            kwargs={"corpid": 2002, "year": 2020, "month": 4},
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertEqual(first=res.context["main_chars"], second={})

    @patch("afat.views.statistics.EveCharacter.objects.filter")
    @patch("afat.views.statistics.get_main_character_from_evecharacter")
    def test_should_accumulate_fats_for_existing_main_character(
        self, mock_get_main_character, mock_character_filter
    ):
        """
        Test that the view accumulates FATs for an existing main character.

        :param mock_get_main_character:
        :param mock_character_filter:
        :return:
        """

        main_character = MagicMock(
            character_id=9999,
            character_name="Main Character",
            corporation_id=2002,
            corporation_name="Wayne Food",
        )
        mock_get_main_character.return_value = main_character
        mock_character_filter.return_value.select_related.return_value = [
            self.character_1003,
            self.character_1004,
        ]

        self.client.force_login(user=self.user_with_stats_corporation_other)

        url = reverse(
            viewname="afat:statistics_corporation",
            kwargs={"corpid": 2002, "year": 2020, "month": 4},
        )
        res = self.client.get(path=url)

        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertEqual(
            first=res.context["main_chars"][9999]["fats"],
            second=2,
        )

    @patch("afat.views.statistics.EveCorporationInfo.objects.filter", return_value=[])
    @patch("afat.views.statistics.get_average_fats_by_corporations", return_value=[])
    @patch("afat.views.statistics.get_fats_per_hour", return_value=[])
    @patch("afat.views.statistics.get_fat_per_weekday", return_value=[])
    @patch("afat.views.statistics.render", return_value=HttpResponse("ok"))
    @patch("afat.views.statistics.get_or_create_alliance_info")
    @patch("afat.views.statistics.Fat.objects.filter")
    def test_should_replace_none_ship_with_unknown_in_alliance_statistics(
        self,
        mock_fat_filter,
        mock_get_alliance,
        _mock_render,
        _mock_weekday,
        _mock_hour,
        _mock_average,
        _mock_corporations,
    ):
        """
        Test that the view replaces None ship with "Unknown" in alliance statistics.

        :param mock_fat_filter:
        :param mock_get_alliance:
        :param _mock_render:
        :param _mock_weekday:
        :param _mock_hour:
        :param _mock_average:
        :param _mock_corporations:
        :return:
        """

        mock_get_alliance.return_value = MagicMock(alliance_name="Test Alliance")

        fake_fat = MagicMock()
        fake_fat.ship.name = None
        fake_fat.character.corporation_name = "Test Corporation"

        mock_queryset = MagicMock()
        mock_queryset.__iter__.return_value = iter([fake_fat])
        mock_queryset.values.return_value.annotate.return_value = []
        mock_fat_filter.return_value = mock_queryset

        self.client.force_login(user=self.user_with_stats_corporation_other)

        response = self.client.get(
            path=reverse(
                viewname="afat:statistics_alliance",
                kwargs={"allianceid": 3001, "year": 2020, "month": 4},
            )
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
        context = _mock_render.call_args.kwargs["context"]
        self.assertEqual(first=context["data_stacked"][0], second=["Test Corporation"])
        self.assertEqual(first=context["data_stacked"][1][0][0], second="Unknown")
