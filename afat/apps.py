"""
App config
"""

# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# Alliance Auth AFAT
from afat import __version__


class AfatConfig(AppConfig):
    """
    General config
    """

    name = "afat"
    label = "afat"
    verbose_name = _(f"AFAT - Another Fleet Activity Tracker v{__version__}")
