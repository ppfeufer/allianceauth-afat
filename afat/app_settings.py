"""
Our app setting
"""

# Django
from django.apps import apps
from django.utils.text import slugify

# Alliance Auth AFAT
from afat import __title__

AFAT_BASE_URL = slugify(value=__title__, allow_unicode=True)


def fittings_installed() -> bool:
    """
    Check if the Fittings module is installed

    :return:
    :rtype:
    """

    return apps.is_installed(app_name="fittings")


def use_fittings_module_for_doctrines() -> bool:
    """
    Check if the Fittings module is used for doctrines

    :return:
    :rtype:
    """

    # Alliance Auth AFAT
    from afat.models import (  # pylint: disable=import-outside-toplevel, cyclic-import
        Setting,
    )

    return (
        fittings_installed() is True
        and Setting.get_setting(Setting.Field.USE_DOCTRINES_FROM_FITTINGS_MODULE)
        is True
    )
