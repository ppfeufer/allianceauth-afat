"""
Test cases for the task in the afat module.
"""

# Standard Library
import unittest
from unittest.mock import ANY, Mock, patch

# Alliance Auth AFAT
from afat.models import FatLink
from afat.tasks import logrotate, update_esi_fatlinks


class TestLogrotateTask(unittest.TestCase):
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


class TestUpdateESIFatlinksTask(unittest.TestCase):
    """
    Test cases for the update_esi_fatlinks task.
    """

    @patch("afat.tasks.fetch_esi_status")
    @patch("afat.tasks.FatLink.objects.select_related_default")
    def test_update_esi_fatlinks_aborts_when_esi_is_offline(
        self, mock_select_related_default, mock_fetch_esi_status
    ):
        """
        Test that the update_esi_fatlinks task aborts when ESI is offline.

        :param mock_select_related_default:
        :type mock_select_related_default:
        :param mock_fetch_esi_status:
        :type mock_fetch_esi_status:
        :return:
        :rtype:
        """

        mock_fetch_esi_status.return_value.is_ok = False

        update_esi_fatlinks()

        mock_select_related_default.assert_not_called()

    @patch("afat.tasks.fetch_esi_status")
    @patch("afat.tasks.FatLink.objects.select_related_default")
    def test_update_esi_fatlinks_processes_fatlinks(
        self, mock_select_related_default, mock_fetch_esi_status
    ):
        """
        Test that the update_esi_fatlinks task processes fatlinks when ESI is online.

        :param mock_select_related_default:
        :type mock_select_related_default:
        :param mock_fetch_esi_status:
        :type mock_fetch_esi_status:
        :return:
        :rtype:
        """

        mock_fetch_esi_status.return_value.is_ok = True
        mock_fatlink = Mock()
        mock_select_related_default.return_value.filter.return_value = [mock_fatlink]

        with patch("afat.tasks._process_esi_fatlink") as mock_process_esi_fatlink:
            update_esi_fatlinks()

            mock_process_esi_fatlink.assert_called_once_with(fatlink=mock_fatlink)

    @patch("afat.tasks.fetch_esi_status")
    @patch("afat.tasks.FatLink.objects.select_related_default")
    def test_update_esi_fatlinks_handles_no_fatlinks(
        self, mock_select_related_default, mock_fetch_esi_status
    ):
        """
        Test that the update_esi_fatlinks task handles the case where there are no fatlinks.

        :param mock_select_related_default:
        :type mock_select_related_default:
        :param mock_fetch_esi_status:
        :type mock_fetch_esi_status:
        :return:
        :rtype:
        """

        mock_fetch_esi_status.return_value.is_ok = True
        mock_select_related_default.return_value.filter.return_value = []

        with patch("afat.tasks._process_esi_fatlink") as mock_process_esi_fatlink:
            update_esi_fatlinks()

            mock_process_esi_fatlink.assert_not_called()

    @patch("afat.tasks.fetch_esi_status")
    @patch("afat.tasks.FatLink.objects.select_related_default")
    def test_update_esi_fatlinks_handles_fatlink_does_not_exist(
        self, mock_select_related_default, mock_fetch_esi_status
    ):
        """
        Test that the update_esi_fatlinks task handles the case where a fatlink does not exist.

        :param mock_select_related_default:
        :type mock_select_related_default:
        :param mock_fetch_esi_status:
        :type mock_fetch_esi_status:
        :return:
        :rtype:
        """

        mock_fetch_esi_status.return_value.is_ok = True
        mock_select_related_default.side_effect = FatLink.DoesNotExist

        update_esi_fatlinks()

        mock_select_related_default.assert_called_once()
