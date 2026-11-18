"""
Test cases for the smart filter model.
"""

# Standard Library
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

# Django
from django.contrib.auth.models import User as BaseAuthUser
from django.db.models.signals import pre_save

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership, User
from allianceauth.authentication.signals import assign_state_on_active_change

# Alliance Auth AFAT
from afat.models.smart_filter import BaseFilter, FatsInTimeFilter, _get_threshold_date
from afat.tests import BaseTestCase


class TestBaseFilter(BaseTestCase):
    """
    Test cases for the BaseFilter class.
    """

    def test_str_returns_name_and_description(self):
        """
        Test that the str method returns the correct string and description.

        :return:
        :rtype:
        """

        obj = type("Dummy", (), {"name": "MyFilter", "description": "Does things"})()

        self.assertEqual(BaseFilter.__str__(obj), "MyFilter: Does things")

    def test_process_filter_raises_not_implemented(self):
        """
        Test that the process_filter method raises an NotImplementedError.

        :return:
        :rtype:
        """

        obj = type("Dummy", (), {})()

        with self.assertRaises(NotImplementedError):
            BaseFilter.process_filter(obj, None)

    def test_audit_filter_raises_not_implemented(self):
        """
        Test that the audit_filter method raises an NotImplementedError.

        :return:
        :rtype:
        """

        obj = type("Dummy", (), {})()

        with self.assertRaises(NotImplementedError):
            BaseFilter.audit_filter(obj, [])


class TestGetThresholdDate(BaseTestCase):
    """
    Test cases for the _get_threshold_date function.
    """

    def test_returns_correct_threshold_date_for_positive_days(self):
        """
        Test that the function returns the correct threshold date for positive days.

        :return:
        :rtype:
        """

        days = 10
        expected_date = datetime.now(timezone.utc) - timedelta(days=days)
        result = _get_threshold_date(days)

        self.assertAlmostEqual(result, expected_date, delta=timedelta(seconds=1))

    def test_returns_correct_threshold_date_for_zero_days(self):
        """
        Test that the function returns the correct threshold date for zero days.

        :return:
        :rtype:
        """

        days = 0
        expected_date = datetime.now(timezone.utc)
        result = _get_threshold_date(days)

        self.assertAlmostEqual(result, expected_date, delta=timedelta(seconds=1))

    def test_does_not_import_queryset_at_runtime(self):
        """
        Test that QuerySet type-only import is not executed at runtime.

        :return:
        :rtype:
        """

        # Alliance Auth AFAT
        import afat.models.smart_filter as smart_filter_module

        self.assertNotIn("QuerySet", smart_filter_module.__dict__)

    def test_type_checking_guard_controls_queryset_import(self):
        """
        Test that QuerySet import is executed only when TYPE_CHECKING is enabled.

        :return:
        :rtype:
        """

        # Standard Library
        import importlib
        import sys

        module_name = "afat.models.smart_filter"

        sys.modules.pop(module_name, None)
        with patch("typing.TYPE_CHECKING", True):
            module_with_type_checking = importlib.import_module(module_name)

        self.assertIn("QuerySet", module_with_type_checking.__dict__)

        sys.modules.pop(module_name, None)
        with patch("typing.TYPE_CHECKING", False):
            module_without_type_checking = importlib.import_module(module_name)

        self.assertNotIn("QuerySet", module_without_type_checking.__dict__)


class TestFatsInTimeFilter(BaseTestCase):
    """
    Test cases for the FatsInTimeFilter class.
    """

    @patch("afat.models.smart_filter._get_threshold_date")
    @patch("afat.models.smart_filter.Fat.objects.filter")
    def test_returns_true_when_user_meets_fats_needed(
        self, mock_fat_filter, mock_get_threshold_date
    ):
        """
        Test that the process_filter method returns True when the user meets the fats needed.

        :param mock_fat_filter:
        :type mock_fat_filter:
        :param mock_get_threshold_date:
        :type mock_get_threshold_date:
        :return:
        :rtype:
        """

        mock_get_threshold_date.return_value = datetime.now(timezone.utc) - timedelta(
            days=30
        )
        mock_fat_filter.return_value.count.return_value = 10
        user = User.objects.create(username="testuser")  # Save the user to the database
        filter_instance = FatsInTimeFilter(days=30, fats_needed=10)
        filter_instance.save()  # Save the filter instance to the database

        self.assertTrue(filter_instance.process_filter(user))

    @patch("afat.models.smart_filter._get_threshold_date")
    @patch("afat.models.smart_filter.Fat.objects.filter")
    def test_returns_false_when_user_does_not_meet_fats_needed(
        self, mock_fat_filter, mock_get_threshold_date
    ):
        """
        Test that the process_filter method returns False when the user does not meet the fats needed.

        :param mock_fat_filter:
        :type mock_fat_filter:
        :param mock_get_threshold_date:
        :type mock_get_threshold_date:
        :return:
        :rtype:
        """

        mock_get_threshold_date.return_value = datetime.now(timezone.utc) - timedelta(
            days=30
        )
        mock_fat_filter.return_value.count.return_value = 5
        user = User.objects.create(username="testuser")  # Save the user to the database
        filter_instance = FatsInTimeFilter(days=30, fats_needed=10)
        filter_instance.save()  # Save the filter instance to the database

        self.assertFalse(filter_instance.process_filter(user))

    @patch("afat.models.smart_filter._get_threshold_date")
    @patch("afat.models.smart_filter.Fat.objects.filter")
    def test_returns_false_when_user_has_no_characters(
        self, mock_fat_filter, mock_get_threshold_date
    ):
        """
        Test that the process_filter method returns False when the user has no characters.

        :param mock_fat_filter:
        :type mock_fat_filter:
        :param mock_get_threshold_date:
        :type mock_get_threshold_date:
        :return:
        :rtype:
        """

        mock_get_threshold_date.return_value = datetime.now(timezone.utc) - timedelta(
            days=30
        )
        mock_fat_filter.side_effect = CharacterOwnership.DoesNotExist
        user = User.objects.create(username="testuser")  # Save the user to the database
        filter_instance = FatsInTimeFilter(days=30, fats_needed=10)
        filter_instance.save()  # Save the filter instance to the database

        self.assertFalse(filter_instance.process_filter(user))

    @patch("afat.models.smart_filter._get_threshold_date")
    @patch("afat.models.smart_filter.Fat.objects.filter")
    def test_returns_correct_audit_results_when_users_have_no_fats(
        self, mock_fat_filter, mock_get_threshold_date
    ):
        """
        Test that the audit_filter method returns the correct results when users have no fats.

        :param mock_fat_filter:
        :type mock_fat_filter:
        :param mock_get_threshold_date:
        :type mock_get_threshold_date:
        :return:
        :rtype:
        """

        mock_get_threshold_date.return_value = datetime.now(timezone.utc) - timedelta(
            days=30
        )

        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.values_list.return_value = []
        mock_fat_filter.return_value = mock_queryset

        # Disconnect the core signal (registered on the base auth User) to avoid
        # triggering it during user creation. Use BaseAuthUser (django's
        # built-in User) as the sender because the core receiver was
        # registered against that class.
        pre_save.disconnect(assign_state_on_active_change, sender=BaseAuthUser)

        user1 = User.objects.create(pk=1, username="user1")
        user2 = User.objects.create(pk=2, username="user2")

        # Reconnect the signal after user creation
        pre_save.connect(assign_state_on_active_change, sender=BaseAuthUser)

        users = [user1, user2]
        filter_instance = FatsInTimeFilter(days=30, fats_needed=2)
        filter_instance.save()
        result = filter_instance.audit_filter(users)

        self.assertEqual(result[1]["message"], 0)
        self.assertFalse(result[1]["check"])
        self.assertEqual(result[2]["message"], 0)
        self.assertFalse(result[2]["check"])

    @patch("afat.models.smart_filter._get_threshold_date")
    @patch("afat.models.smart_filter.Fat.objects.filter")
    @patch("afat.models.smart_filter.FatsInTimeFilter.fleet_types")
    @patch("afat.models.smart_filter.FatsInTimeFilter.ship_classes")
    def test_returns_true_when_optional_filters_are_empty_and_count_meets_threshold(
        self,
        mock_ship_classes,
        mock_fleet_types,
        mock_fat_filter,
        mock_get_threshold_date,
    ):
        """
        Verify process_filter returns True when optional ship and fleet filters are empty.

        :param mock_fat_filter:
        :type mock_fat_filter:
        :param mock_get_threshold_date:
        :type mock_get_threshold_date:
        :return:
        :rtype:
        """

        mock_get_threshold_date.return_value = datetime.now(timezone.utc) - timedelta(
            days=30
        )

        fat_queryset = MagicMock()
        fat_queryset.count.return_value = 3
        mock_fat_filter.return_value = fat_queryset

        empty_ship_classes = MagicMock()
        empty_ship_classes.exists.return_value = False
        empty_fleet_types = MagicMock()
        empty_fleet_types.exists.return_value = False

        filter_instance = FatsInTimeFilter.objects.create(days=30, fats_needed=3)
        mock_ship_classes.all.return_value.values_list.return_value = empty_ship_classes
        mock_fleet_types.all.return_value.values_list.return_value = empty_fleet_types

        user = User.objects.create(username="counting-user")

        self.assertTrue(filter_instance.process_filter(user))
        fat_queryset.filter.assert_not_called()

    @patch("afat.models.smart_filter._get_threshold_date")
    @patch("afat.models.smart_filter.Fat.objects.filter")
    @patch("afat.models.smart_filter.FatsInTimeFilter.fleet_types")
    @patch("afat.models.smart_filter.FatsInTimeFilter.ship_classes")
    def test_applies_ship_and_fleet_filters_when_selected(
        self,
        mock_ship_classes,
        mock_fleet_types,
        mock_fat_filter,
        mock_get_threshold_date,
    ):
        """
        Verify process_filter applies selected ship and fleet constraints before counting.

        :param mock_fat_filter:
        :type mock_fat_filter:
        :param mock_get_threshold_date:
        :type mock_get_threshold_date:
        :return:
        :rtype:
        """

        mock_get_threshold_date.return_value = datetime.now(timezone.utc) - timedelta(
            days=7
        )

        filtered_by_ship = MagicMock()
        filtered_by_fleet = MagicMock()
        filtered_by_fleet.count.return_value = 2

        base_fat_queryset = MagicMock()
        base_fat_queryset.filter.return_value = filtered_by_ship
        filtered_by_ship.filter.return_value = filtered_by_fleet
        mock_fat_filter.return_value = base_fat_queryset

        selected_ship_classes = MagicMock()
        selected_ship_classes.exists.return_value = True
        selected_fleet_types = MagicMock()
        selected_fleet_types.exists.return_value = True

        filter_instance = FatsInTimeFilter.objects.create(days=7, fats_needed=2)
        mock_ship_classes.all.return_value.values_list.return_value = (
            selected_ship_classes
        )
        mock_fleet_types.all.return_value.values_list.return_value = (
            selected_fleet_types
        )

        user = User.objects.create(username="filtered-user")

        self.assertTrue(filter_instance.process_filter(user))
        base_fat_queryset.filter.assert_any_call(shiptype__in=selected_ship_classes)
        filtered_by_ship.filter.assert_any_call(
            fatlink__fleet_type__in=selected_fleet_types
        )

    @patch("afat.models.smart_filter._get_threshold_date")
    @patch("afat.models.smart_filter.CharacterOwnership.objects.filter")
    @patch("afat.models.smart_filter.Fat.objects.filter")
    @patch("afat.models.smart_filter.FatsInTimeFilter.fleet_types")
    @patch("afat.models.smart_filter.FatsInTimeFilter.ship_classes")
    def test_returns_audit_status_for_users_with_and_without_matching_fats(
        self,
        mock_ship_classes,
        mock_fleet_types,
        mock_fat_filter,
        mock_character_ownership_filter,
        mock_get_threshold_date,
    ):
        """
        Verify audit_filter returns pass/fail and counts for mixed user FAT results.

        :param mock_fat_filter:
        :type mock_fat_filter:
        :param mock_character_ownership_filter:
        :type mock_character_ownership_filter:
        :param mock_get_threshold_date:
        :type mock_get_threshold_date:
        :return:
        :rtype:
        """

        mock_get_threshold_date.return_value = datetime.now(timezone.utc) - timedelta(
            days=14
        )

        character_queryset = MagicMock()
        character_queryset.values.return_value = [{"character": 1}, {"character": 2}]
        mock_character_ownership_filter.return_value = character_queryset

        user1 = User.objects.create(username="audit-user-1")
        user2 = User.objects.create(username="audit-user-2")
        user3 = User.objects.create(username="audit-user-3")

        fat1 = MagicMock()
        fat1.pk = 100
        fat1.character.character_ownership.user.pk = user1.pk

        fat2 = MagicMock()
        fat2.pk = 101
        fat2.character.character_ownership.user.pk = user1.pk

        fat3 = MagicMock()
        fat3.pk = 102
        fat3.character.character_ownership.user.pk = user2.pk

        fat_queryset = MagicMock()
        fat_queryset.select_related.return_value = fat_queryset
        fat_queryset.__iter__.return_value = iter([fat1, fat2, fat3])

        empty_ship_classes = MagicMock()
        empty_ship_classes.exists.return_value = False
        empty_fleet_types = MagicMock()
        empty_fleet_types.exists.return_value = False

        mock_fat_filter.return_value = fat_queryset

        filter_instance = FatsInTimeFilter.objects.create(days=14, fats_needed=2)
        mock_ship_classes.all.return_value.values_list.return_value = empty_ship_classes
        mock_fleet_types.all.return_value.values_list.return_value = empty_fleet_types

        result = filter_instance.audit_filter([user1, user2, user3])

        self.assertEqual(result[user1.pk]["message"], 2)
        self.assertTrue(result[user1.pk]["check"])

        self.assertEqual(result[user2.pk]["message"], 1)
        self.assertFalse(result[user2.pk]["check"])

        self.assertEqual(result[user3.pk]["message"], 0)
        self.assertFalse(result[user3.pk]["check"])

    @patch("afat.models.smart_filter._get_threshold_date")
    @patch("afat.models.smart_filter.CharacterOwnership.objects.filter")
    @patch("afat.models.smart_filter.Fat.objects.filter")
    @patch("afat.models.smart_filter.FatsInTimeFilter.fleet_types")
    @patch("afat.models.smart_filter.FatsInTimeFilter.ship_classes")
    def test_audit_applies_ship_class_filter_when_ship_classes_exist(
        self,
        mock_ship_classes,
        mock_fleet_types,
        mock_fat_filter,
        mock_character_ownership_filter,
        mock_get_threshold_date,
    ):
        """
        Verify audit_filter applies shiptype filtering when ship classes are configured.

        :return:
        :rtype:
        """

        mock_get_threshold_date.return_value = datetime.now(timezone.utc) - timedelta(
            days=30
        )

        character_queryset = MagicMock()
        character_queryset.values.return_value = [{"character": 1}, {"character": 2}]
        mock_character_ownership_filter.return_value = character_queryset

        ship_classes = MagicMock()
        ship_classes.exists.return_value = True
        fleet_types = MagicMock()
        fleet_types.exists.return_value = False
        mock_ship_classes.all.return_value.values_list.return_value = ship_classes
        mock_fleet_types.all.return_value.values_list.return_value = fleet_types

        user1 = User.objects.create(username="audit-ship-user-1")
        user2 = User.objects.create(username="audit-ship-user-2")

        fat1 = MagicMock()
        fat1.pk = 200
        fat1.character.character_ownership.user.pk = user1.pk

        base_fats = MagicMock()
        base_fats.select_related.return_value = base_fats
        base_fats.__iter__.side_effect = AssertionError(
            "unfiltered queryset should not be iterated"
        )

        filtered_fats = MagicMock()
        filtered_fats.__iter__.return_value = iter([fat1])

        base_fats.filter.return_value = filtered_fats
        mock_fat_filter.return_value = base_fats

        filter_instance = FatsInTimeFilter.objects.create(days=30, fats_needed=1)

        result = filter_instance.audit_filter([user1, user2])

        base_fats.filter.assert_called_once_with(shiptype__in=ship_classes)
        self.assertEqual(result[user1.pk]["message"], 1)
        self.assertTrue(result[user1.pk]["check"])
        self.assertEqual(result[user2.pk]["message"], 0)
        self.assertFalse(result[user2.pk]["check"])

    @patch("afat.models.smart_filter._get_threshold_date")
    @patch("afat.models.smart_filter.Fat.objects.filter")
    @patch("afat.models.smart_filter.FatsInTimeFilter.fleet_types")
    @patch("afat.models.smart_filter.FatsInTimeFilter.ship_classes")
    def test_applies_ship_class_filter_when_ship_classes_exist(
        self,
        mock_ship_classes,
        mock_fleet_types,
        mock_fat_filter,
        mock_get_threshold_date,
    ):
        """
        Verify process_filter uses ship class filtering when ship classes are configured.

        :return:
        :rtype:
        """

        mock_get_threshold_date.return_value = datetime.now(timezone.utc) - timedelta(
            days=30
        )

        ship_classes = MagicMock()
        ship_classes.exists.return_value = True
        fleet_types = MagicMock()
        fleet_types.exists.return_value = False

        unfiltered_fats = MagicMock()
        unfiltered_fats.count.return_value = 2
        filtered_fats = MagicMock()
        filtered_fats.count.return_value = 1
        unfiltered_fats.filter.return_value = filtered_fats
        mock_fat_filter.return_value = unfiltered_fats

        filter_instance = FatsInTimeFilter.objects.create(days=30, fats_needed=2)
        mock_ship_classes.all.return_value.values_list.return_value = ship_classes
        mock_fleet_types.all.return_value.values_list.return_value = fleet_types

        user = User.objects.create(username="branch-user")

        self.assertFalse(filter_instance.process_filter(user))
        unfiltered_fats.filter.assert_called_once_with(shiptype__in=ship_classes)
        unfiltered_fats.count.assert_not_called()
        filtered_fats.count.assert_called_once_with()

    @patch("afat.models.smart_filter._get_threshold_date")
    @patch("afat.models.smart_filter.Fat.objects.filter")
    @patch("afat.models.smart_filter.FatsInTimeFilter.fleet_types")
    @patch("afat.models.smart_filter.FatsInTimeFilter.ship_classes")
    def test_applies_fleet_type_filter_when_fleet_types_exist(
        self,
        mock_ship_classes,
        mock_fleet_types,
        mock_fat_filter,
        mock_get_threshold_date,
    ):
        """
        Verify process_filter applies fleet type filtering when fleet types are configured.

        :return:
        :rtype:
        """

        mock_get_threshold_date.return_value = datetime.now(timezone.utc) - timedelta(
            days=30
        )

        ship_classes = MagicMock()
        ship_classes.exists.return_value = False
        fleet_types = MagicMock()
        fleet_types.exists.return_value = True

        unfiltered_fats = MagicMock()
        unfiltered_fats.count.return_value = 2
        filtered_fats = MagicMock()
        filtered_fats.count.return_value = 1
        unfiltered_fats.filter.return_value = filtered_fats
        mock_fat_filter.return_value = unfiltered_fats

        filter_instance = FatsInTimeFilter.objects.create(days=30, fats_needed=2)
        mock_ship_classes.all.return_value.values_list.return_value = ship_classes
        mock_fleet_types.all.return_value.values_list.return_value = fleet_types

        user = User.objects.create(username="fleet-branch-user")

        self.assertFalse(filter_instance.process_filter(user))
        unfiltered_fats.filter.assert_called_once_with(
            fatlink__fleet_type__in=fleet_types
        )
        unfiltered_fats.count.assert_not_called()
        filtered_fats.count.assert_called_once_with()

    @patch("afat.models.smart_filter._get_threshold_date")
    @patch("afat.models.smart_filter.CharacterOwnership.objects.filter")
    @patch("afat.models.smart_filter.Fat.objects.filter")
    @patch("afat.models.smart_filter.FatsInTimeFilter.fleet_types")
    @patch("afat.models.smart_filter.FatsInTimeFilter.ship_classes")
    def test_audit_applies_fleet_type_filter_when_fleet_types_exist(
        self,
        mock_ship_classes,
        mock_fleet_types,
        mock_fat_filter,
        mock_character_ownership_filter,
        mock_get_threshold_date,
    ):
        """
        Verify audit_filter applies fleet type filtering when fleet types are configured.

        :return:
        :rtype:
        """

        mock_get_threshold_date.return_value = datetime.now(timezone.utc) - timedelta(
            days=30
        )

        character_queryset = MagicMock()
        character_queryset.values.return_value = [{"character": 1}, {"character": 2}]
        mock_character_ownership_filter.return_value = character_queryset

        ship_classes = MagicMock()
        ship_classes.exists.return_value = False
        fleet_types = MagicMock()
        fleet_types.exists.return_value = True
        mock_ship_classes.all.return_value.values_list.return_value = ship_classes
        mock_fleet_types.all.return_value.values_list.return_value = fleet_types

        user1 = User.objects.create(username="audit-fleet-user-1")
        user2 = User.objects.create(username="audit-fleet-user-2")

        fat1 = MagicMock()
        fat1.pk = 300
        fat1.character.character_ownership.user.pk = user1.pk

        base_fats = MagicMock()
        base_fats.select_related.return_value = base_fats
        base_fats.__iter__.side_effect = AssertionError(
            "unfiltered queryset should not be iterated"
        )

        filtered_fats = MagicMock()
        filtered_fats.__iter__.return_value = iter([fat1])

        base_fats.filter.return_value = filtered_fats
        mock_fat_filter.return_value = base_fats

        filter_instance = FatsInTimeFilter.objects.create(days=30, fats_needed=1)

        result = filter_instance.audit_filter([user1, user2])

        base_fats.filter.assert_called_once_with(fatlink__fleet_type__in=fleet_types)
        self.assertEqual(result[user1.pk]["message"], 1)
        self.assertTrue(result[user1.pk]["check"])
        self.assertEqual(result[user2.pk]["message"], 0)
        self.assertFalse(result[user2.pk]["check"])
