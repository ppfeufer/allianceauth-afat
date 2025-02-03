"""
Constants used in this module
"""

# Standard Library
import os

# Alliance Auth
from esi import __version__ as esi_version

# Alliance Auth AFAT
from afat import __version__

APP_NAME = "allianceauth-afat"
GITHUB_URL = f"https://github.com/ppfeufer/{APP_NAME}"
USER_AGENT = f"{APP_NAME}/{__version__} ({GITHUB_URL}) via django-esi/{esi_version}"
INTERNAL_URL_PREFIX = "-"

# aa-srp/aasrp
AFAT_BASE_DIR = os.path.join(os.path.dirname(__file__))
# aa-srp/aasrp/static/aasrp
AFAT_STATIC_DIR = os.path.join(AFAT_BASE_DIR, "static", "afat")
