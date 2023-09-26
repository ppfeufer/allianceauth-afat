# Standard Library
from http import HTTPStatus
from unittest.mock import Mock

# Django
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from app_utils.testing import add_character_to_user, create_user_from_evecharacter

# Alliance Auth AFAT
from afat.models import Fat, FatLink
from afat.tests.fixtures.load_allianceauth import load_allianceauth
from afat.views.dashboard import overview

MODULE_PATH = "afat.views.dashboard"


def response_content_to_str(response) -> str:
    return response.content.decode(response.charset)


class TestDashboard(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
        load_allianceauth()

        # given
        cls.character_1001 = EveCharacter.objects.get(character_id=1001)
        cls.character_1002 = EveCharacter.objects.get(character_id=1002)
        cls.character_1101 = EveCharacter.objects.get(character_id=1101)

        cls.user, _ = create_user_from_evecharacter(
            character_id=cls.character_1001.character_id,
            permissions=["afat.basic_access"],
        )

        add_character_to_user(user=cls.user, character=cls.character_1101)

        create_user_from_evecharacter(character_id=cls.character_1002.character_id)

        cls.afat_link = FatLink.objects.create(
            fleet="Demo Fleet",
            hash="123",
            creator=cls.user,
            character=cls.character_1001,
        )

    def _page_overview_request(self, user):
        request = self.factory.get(path=reverse(viewname="afat:dashboard"))
        request.user = user

        middleware = SessionMiddleware(get_response=Mock())
        middleware.process_request(request=request)

        return overview(request)

    def test_should_only_show_my_chars_and_only_those_with_fat_links(self):
        # given
        Fat.objects.create(character=self.character_1101, fatlink=self.afat_link)
        Fat.objects.create(character=self.character_1002, fatlink=self.afat_link)

        # when
        response = self._page_overview_request(user=self.user)

        # then
        content = response_content_to_str(response=response)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(
            member=f'<span id="afat-eve-character-id-{self.character_1101.character_id}">{self.character_1101.character_name}</span>',
            container=content,
        )
        self.assertNotIn(
            member=f'<span id="afat-eve-character-id-{self.character_1001.character_id}">{self.character_1001.character_name}</span>',
            container=content,
        )
        self.assertNotIn(
            member=f'<span id="afat-eve-character-id-{self.character_1002.character_id}">{self.character_1002.character_name}</span>',
            container=content,
        )
