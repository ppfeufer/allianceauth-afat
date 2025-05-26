"""
Constants used in this module
"""

# Django
from django.utils.text import slugify

# Alliance Auth
from esi import __version__ as esi_version

# Alliance Auth AFAT
from afat import __title__, __version__

APP_NAME = "allianceauth-afat"
APP_NAME_VERBOSE = "Alliance Auth AFAT"
APP_NAME_USERAGENT = "Alliance-Auth-AFAT"
APP_BASE_URL = slugify(value=__title__, allow_unicode=True)

PACKAGE_NAME = "afat"
DJANGO_ESI_URL = "https://gitlab.com/allianceauth/django-esi"

GITHUB_URL = f"https://github.com/ppfeufer/{APP_NAME}"
USER_AGENT = f"{APP_NAME_USERAGENT}/{__version__} (+{GITHUB_URL}) Django-ESI/{esi_version} (+{DJANGO_ESI_URL})"

INTERNAL_URL_PREFIX = "-"
