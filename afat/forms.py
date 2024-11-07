"""
The forms we use
"""

# Django
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# Alliance Auth AFAT
from afat.app_settings import AFAT_DEFAULT_FATLINK_EXPIRY_TIME
from afat.helper.fatlinks import get_doctrines
from afat.models import Doctrine, FleetType, Setting

# The first line dropdown is blank
# Usage example: dropdown = form_choices_blank + [(o.id, o.name) for o in objects]
form_choices_blank = [("", "---------")]


def get_mandatory_form_label_text(text):
    """
    Label text for mandatory form fields

    :param text:
    :type text:
    :return:
    :rtype:
    """

    required_text = _("This field is mandatory")
    required_marker = (
        f'<span aria-label="{required_text}" class="form-required-marker">*</span>'
    )

    return mark_safe(
        f'<span class="form-field-required">{text} {required_marker}</span>'
    )


class AFatEsiFatForm(forms.Form):
    """
    Fat link form
    Used to create ESI fatlinks
    """

    name_esi = forms.CharField(
        required=True,
        label=get_mandatory_form_label_text(text=_("Fleet name")),
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": _("Enter fleet name")}),
    )
    type_esi = forms.ModelChoiceField(
        required=False,
        label=_("Fleet type (optional)"),
        queryset=FleetType.objects.filter(is_enabled=True),
    )
    doctrine_esi = forms.ChoiceField(
        required=False,
        label=_("Doctrine (optional)"),
        choices=(),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # Due to the dynamic nature of this dropdown field, we need to initialize it here.
        # This is a workaround to avoid settings being cached and not updated when changed.
        # This is also the reason we cannot use a ModelChoiceField here.
        self.fields["doctrine_esi"].choices = form_choices_blank + [
            (str(o), str(o)) for o in get_doctrines()
        ]


class AFatManualFatForm(forms.Form):
    """
    Manual fat form
    """

    character = forms.CharField(
        required=True,
        label=get_mandatory_form_label_text(text=_("Character Name")),
        max_length=255,
    )
    system = forms.CharField(
        required=True,
        label=get_mandatory_form_label_text(text=_("System")),
        max_length=100,
    )
    shiptype = forms.CharField(
        required=True,
        label=get_mandatory_form_label_text(text=_("Ship type")),
        max_length=100,
    )


class AFatClickFatForm(forms.Form):
    """
    Fat link form
    Used to create clickable fatlinks
    """

    name = forms.CharField(
        required=True,
        label=get_mandatory_form_label_text(text=_("Fleet name")),
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": _("Enter fleet name")}),
    )
    type = forms.ModelChoiceField(
        required=False,
        label=_("Fleet type (optional)"),
        queryset=FleetType.objects.filter(is_enabled=True),
    )
    doctrine = forms.ChoiceField(
        required=False,
        label=_("Doctrine (optional)"),
        choices=(),
    )
    duration = forms.IntegerField(
        required=True,
        label=get_mandatory_form_label_text(text=_("FAT link expiry time in minutes")),
        min_value=1,
        initial=AFAT_DEFAULT_FATLINK_EXPIRY_TIME,
        widget=forms.TextInput(attrs={"placeholder": _("Expiry time in minutes")}),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # Due to the dynamic nature of this dropdown field, we need to initialize it here.
        # This is a workaround to avoid settings being cached and not updated when changed.
        # This is also the reason we cannot use a ModelChoiceField here.
        self.fields["doctrine"].choices = form_choices_blank + [
            (str(o), str(o)) for o in get_doctrines()
        ]


class FatLinkEditForm(forms.Form):
    """
    Fat link edit form
    Used in edit view to change the fat link name
    """

    fleet = forms.CharField(
        required=True,
        label=get_mandatory_form_label_text(text=_("Fleet name")),
        max_length=255,
    )


class SettingAdminForm(forms.ModelForm):
    """
    Form definitions for the FleetType form
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta
        """

        model = Setting

        fields = "__all__"


class DoctrineAdminForm(forms.ModelForm):
    """
    Form definitions for the Doctrine form
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta
        """

        model = Doctrine

        fields = "__all__"
