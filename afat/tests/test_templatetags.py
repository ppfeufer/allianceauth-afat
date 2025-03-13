"""
Test our template tags
"""

# Django
from django.template import Context, Template
from django.test import TestCase, override_settings

# Alliance Auth AFAT
from afat import __version__
from afat.constants import PACKAGE_NAME
from afat.helper.static_files import calculate_integrity_hash


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

    @override_settings(DEBUG=False)
    def test_versioned_static(self):
        """
        Test should return the versioned static

        :return:
        :rtype:
        """

        context = Context(dict_={"version": __version__})
        template_to_render = Template(
            template_string=(
                "{% load afat %}"
                "{% afat_static 'css/afat.min.css' %}"
                "{% afat_static 'javascript/afat.min.js' %}"
            )
        )

        rendered_template = template_to_render.render(context=context)

        expected_static_css_src = (
            f'/static/{PACKAGE_NAME}/css/afat.min.css?v={context["version"]}'
        )
        expected_static_css_src_integrity = calculate_integrity_hash("css/afat.min.css")
        expected_static_js_src = (
            f'/static/{PACKAGE_NAME}/javascript/afat.min.js?v={context["version"]}'
        )
        expected_static_js_src_integrity = calculate_integrity_hash(
            "javascript/afat.min.js"
        )

        self.assertIn(member=expected_static_css_src, container=rendered_template)
        self.assertIn(
            member=expected_static_css_src_integrity, container=rendered_template
        )
        self.assertIn(member=expected_static_js_src, container=rendered_template)
        self.assertIn(
            member=expected_static_js_src_integrity, container=rendered_template
        )

    @override_settings(DEBUG=True)
    def test_versioned_static_with_debug_enabled(self) -> None:
        """
        Test versioned static template tag with DEBUG enabled

        :return:
        :rtype:
        """

        context = Context({"version": __version__})
        template_to_render = Template(
            template_string=("{% load afat %}" "{% afat_static 'css/afat.min.css' %}")
        )

        rendered_template = template_to_render.render(context=context)

        expected_static_css_src = (
            f'/static/{PACKAGE_NAME}/css/afat.min.css?v={context["version"]}'
        )

        self.assertIn(member=expected_static_css_src, container=rendered_template)
        self.assertNotIn(member="integrity=", container=rendered_template)

    @override_settings(DEBUG=False)
    def test_invalid_file_type(self) -> None:
        """
        Test should raise a ValueError for an invalid file type

        :return:
        :rtype:
        """

        context = Context({"version": __version__})
        template_to_render = Template(
            template_string=(
                "{% load afat %}" "{% afat_static 'invalid/invalid.txt' %}"
            )
        )

        with self.assertRaises(ValueError):
            template_to_render.render(context=context)


class SumValuesFilterTest(TestCase):
    """
    Test the sum_values filter
    """

    def test_sum_values(self):
        """
        Test sum_values

        :return:
        :rtype:
        """

        context = Context(dict_={"test_dict": {"a": 1, "b": 2, "c": 3}})
        template_to_render = Template(
            template_string="{% load afat %} {{ test_dict|sum_values }}"
        )

        rendered_template = template_to_render.render(context=context)

        self.assertInHTML(needle="6", haystack=rendered_template)
