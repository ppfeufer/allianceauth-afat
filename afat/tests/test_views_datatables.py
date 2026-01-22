"""
Tests for DataTables views.
"""

# Django
from django.test import RequestFactory
from django.utils.datetime_safe import datetime

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth AFAT
from afat.models import FatLink
from afat.tests import BaseTestCase
from afat.tests.fixtures.utils import create_user_from_evecharacter
from afat.views.datatables import FatLinksTableView


class TestFatLinksTableView(BaseTestCase):
    """
    Tests for FatLinksTableView.
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

        cls.user_without_access, _ = create_user_from_evecharacter(
            character_id=cls.character_1001.character_id
        )

        cls.user_with_basic_access, _ = create_user_from_evecharacter(
            character_id=cls.character_1002.character_id,
            permissions=["afat.basic_access"],
        )

        # Setup some FAT links
        cls.fatlink1 = FatLink.objects.create(
            created="2023-03-15",
            fleet="Fleet Alpha",
            creator=cls.user_with_basic_access,
            hash="abc123",
        )
        cls.fatlink2 = FatLink.objects.create(
            created="2022-11-20",
            fleet="Fleet Beta",
            creator=cls.user_with_basic_access,
            hash="def456",
        )
        cls.fatlink3 = FatLink.objects.create(
            created="2023-07-05",
            fleet="Fleet Gamma",
            creator=cls.user_with_basic_access,
            hash="ghi789",
        )
        cls.fatlink_current_year1 = FatLink.objects.create(
            created=datetime.now(),
            fleet="Fleet Delta",
            creator=cls.user_with_basic_access,
            hash="jkl012",
        )
        cls.fatlink_current_year2 = FatLink.objects.create(
            created=datetime.now(),
            fleet="Fleet Epsilon",
            creator=cls.user_with_basic_access,
            hash="mno345",
        )

    def test_returns_correct_queryset_for_current_year(self):
        """
        Test returns correct queryset for current year

        :return:
        :rtype:
        """

        request = RequestFactory().get("/")
        view = FatLinksTableView()
        qs = view.get_model_qs(request)

        self.assertEqual(qs.count(), 2)

    def test_returns_correct_queryset_for_specific_year(self):
        """
        Test returns correct queryset for specific year

        :return:
        :rtype:
        """

        request = RequestFactory().get("/")
        view = FatLinksTableView()
        qs = view.get_model_qs(request, year=2022)

        self.assertEqual(qs.count(), 1)

    # @patch("afat.models.FatLink.objects.select_related_default")
    # def test_calls_select_related_default_on_queryset(self, mock_select_related):
    #     """
    #     Test calls select_related_default on queryset
    #
    #     :param mock_select_related:
    #     :type mock_select_related:
    #     :return:
    #     :rtype:
    #     """
    #
    #     mock_select_related.return_value.filter.return_value.annotate_fats_count.return_value = (
    #         []
    #     )
    #     request = RequestFactory().get("/")
    #     view = FatLinksTableView()
    #     view.get_model_qs(request)
    #
    #     mock_select_related.assert_called_once()
