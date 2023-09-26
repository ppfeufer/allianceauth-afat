"""
App config
"""

# Standard Library
from importlib import metadata

# Django
from django.utils.translation import gettext_lazy as _

__version__ = metadata.version(distribution_name="allianceauth-afat")

del metadata

__title__ = _("Fleet Activity Tracking")
