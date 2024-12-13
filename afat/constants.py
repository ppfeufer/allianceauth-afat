"""
Constants used in this module
"""

# Alliance Auth
from esi import __version__ as esi_version

# Alliance Auth AFAT
from afat import __version__

APP_NAME = "allianceauth-afat"
GITHUB_URL = f"https://github.com/ppfeufer/{APP_NAME}"
USER_AGENT = f"{APP_NAME}/{__version__} ({GITHUB_URL}) via django-esi/{esi_version}"
INTERNAL_URL_PREFIX = "-"
