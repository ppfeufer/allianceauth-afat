"""
Our app setting
"""

# Third Party
import unidecode

# Django
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# Alliance Auth (External Libs)
from app_utils.app_settings import clean_setting

# Set default expiry time in minutes
AFAT_DEFAULT_FATLINK_EXPIRY_TIME = clean_setting(
    name="AFAT_DEFAULT_FATLINK_EXPIRY_TIME", default_value=60
)

# Set the default time in minutes a FAT lnk can be re-opened after it is expired
AFAT_DEFAULT_FATLINK_REOPEN_GRACE_TIME = clean_setting(
    name="AFAT_DEFAULT_FATLINK_REOPEN_GRACE_TIME", default_value=60
)

# Set the default time in minutes a FAT link is re-opened for
AFAT_DEFAULT_FATLINK_REOPEN_DURATION = clean_setting(
    name="AFAT_DEFAULT_FATLINK_REOPEN_DURATION", default_value=60
)

AFAT_DEFAULT_LOG_DURATION = clean_setting(
    name="AFAT_DEFAULT_LOG_DURATION", default_value=60
)

# Name of this app, as shown in the Auth sidebar and page titles
AFAT_APP_NAME = clean_setting(
    name="AFAT_APP_NAME", default_value=_("Fleet Activity Tracking"), required_type=str
)

AFAT_BASE_URL = slugify(unidecode.unidecode(AFAT_APP_NAME), allow_unicode=True)
