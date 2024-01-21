"""
Test our template tags
"""

# Django
from django.template import Context, Template
from django.test import TestCase

# Alliance Auth AFAT
from afat import __version__


class TestAfatFilters(TestCase):
    """
    Test template filters
    """

    def test_month_name_filter(self):
        """
        Test month_name

        :return:
        """

        context = Context(dict_={"month": 5})
        template_to_render = Template(
            template_string="{% load afat %} {{ month|month_name }}"
        )

        rendered_template = template_to_render.render(context=context)

        self.assertInHTML(needle="May", haystack=rendered_template)


class TestAfatStatic(TestCase):
    """
    Test versioned static template tag
    """

    def test_afat_static(self):
        """
        Test afat_static

        :return:
        """

        context = Context(dict_={"version": __version__})
        template_to_render = Template(
            template_string=(
                "{% load afat %}"
                "{% afat_static 'afat/css/allianceauth-afat.min.css' %}"
            )
        )

        rendered_template = template_to_render.render(context=context)

        self.assertInHTML(
            needle=f'/static/afat/css/allianceauth-afat.min.css?v={context["version"]}',
            haystack=rendered_template,
        )
