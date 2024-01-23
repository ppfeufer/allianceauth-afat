"""
Auth hooks
"""

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

# Alliance Auth AFAT
from afat import urls
from afat.app_settings import AFAT_APP_NAME, AFAT_BASE_URL


class AaAfatMenuItem(MenuItemHook):  # pylint: disable=too-few-public-methods
    """
    This class ensures only authorized users will see the menu entry
    """

    def __init__(self):
        # Setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            text=AFAT_APP_NAME,
            classes="fa-solid fa-space-shuttle",
            url_name="afat:dashboard",
            navactive=["afat:"],
        )

    def render(self, request):
        """
        Only if the user has access to this app

        :param request:
        :type request:
        :return:
        :rtype:
        """

        if request.user.has_perm(perm="afat.basic_access"):
            return MenuItemHook.render(self, request=request)

        return ""


@hooks.register(name="menu_item_hook")
def register_menu():
    """
    Register our menu

    :return:
    :rtype:
    """

    return AaAfatMenuItem()


@hooks.register(name="url_hook")
def register_url():
    """
    Register our menu link

    :return:
    :rtype:
    """

    return UrlHook(urls=urls, namespace="afat", base_url=rf"^{AFAT_BASE_URL}/")
