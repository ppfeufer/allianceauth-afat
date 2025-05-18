"""
Test cases for the smart filter model.
"""

# Standard Library
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

# Django
from django.contrib.auth.models import User
from django.test import TestCase

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership

# Alliance Auth AFAT
from afat.models.smart_filter import FatsInTimeFilter, _get_threshold_date


class TestGetThresholdDate(TestCase):
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


class TestFatsInTimeFilter(TestCase):
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

        self.assertFalse(filter_instance.process_filter(user))
