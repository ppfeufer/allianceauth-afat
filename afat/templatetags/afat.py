"""
Versioned static URLs to break browser caches when changing the app version.
"""

# Standard Library
import os

# Django
from django.template.defaulttags import register
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# Alliance Auth AFAT
from afat import __title__, __version__
from afat.app_settings import debug_enabled
from afat.constants import PACKAGE_NAME
from afat.helper.static_files import calculate_integrity_hash

logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


@register.simple_tag
def afat_static(relative_file_path: str, script_type: str = None) -> str | None:
    """
    Versioned static URL

    :param relative_file_path: The file path relative to the `{APP_NAME}/{PACKAGE_NAME}/static/{PACKAGE_NAME}` folder
    :type relative_file_path: str
    :param script_type: The script type
    :type script_type: str
    :return: Versioned static URL
    :rtype: str
    """

    logger.debug(f"Getting versioned static URL for: {relative_file_path}")

    file_type = os.path.splitext(relative_file_path)[1][1:]

    logger.debug(f"File extension: {file_type}")

    # Only support CSS and JS files
    if file_type not in ["css", "js"]:
        raise ValueError(f"Unsupported file type: {file_type}")

    static_file_path = os.path.join(PACKAGE_NAME, relative_file_path)
    static_url = static(static_file_path)

    # Integrity hash calculation only for non-debug mode
    sri_string = (
        f' integrity="{calculate_integrity_hash(relative_file_path)}" crossorigin="anonymous"'
        if not debug_enabled()
        else ""
    )

    # Versioned URL for CSS and JS files
    # Add version query parameter to break browser caches when changing the app version
    # Do not add version query parameter for libs as they are already versioned through their file path
    versioned_url = (
        static_url
        if relative_file_path.startswith("libs/")
        else static_url + "?v=" + __version__
    )

    return_value = None

    # Return the versioned URL with integrity hash for CSS
    if file_type == "css":
        return_value = mark_safe(
            f'<link rel="stylesheet" href="{versioned_url}"{sri_string}>'
        )

    # Return the versioned URL with integrity hash for JS files
    if file_type == "js":
        js_type = f' type="{script_type}"' if script_type else ""

        return_value = mark_safe(
            f'<script{js_type} src="{versioned_url}"{sri_string}></script>'
        )

    return return_value


@register.filter
def month_name(month_number):
    """
    Template tag :: get month name from month number
    example: {{ event.month|month_name }}

    :param month_number:
    :return:
    """

    month_mapper = {
        1: _("January"),
        2: _("February"),
        3: _("March"),
        4: _("April"),
        5: _("May"),
        6: _("June"),
        7: _("July"),
        8: _("August"),
        9: _("September"),
        10: _("October"),
        11: _("November"),
        12: _("December"),
    }

    return month_mapper[int(month_number)]


@register.filter
def sum_values(dictionary):
    """
    Template tag :: sum all values in a dictionary
    example: {{ dictionary|sum_values }}

    :param dictionary:
    :type dictionary:
    :return:
    :rtype:
    """

    return sum(dictionary.values())
