from django import forms
from django.conf import settings
from django.forms.models import inlineformset_factory

from us_ignite.common import output
from us_ignite.events.models import Audience, Event, EventURL
from us_ignite.hubs.models import Hub
from us_ignite.organizations.models import Organization


def _get_status_choices():
    """Returns a list of valid user status for the ``Event``"""
    available_status = [
        Event.PUBLISHED,
        Event.DRAFT,
    ]
    is_valid_status = lambda x: x[0] in available_status
    return filter(is_valid_status, Event.STATUS_CHOICES)


DATE_HELP_TEXT = 'Format: YYYY-MM-DD HH:MM'


class EventForm(forms.ModelForm):
    start_datetime = forms.DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS, help_text=DATE_HELP_TEXT)
    end_datetime = forms.DateTimeField(
        input_formats=settings.DATETIME_INPUT_FORMATS, required=False,
        help_text=DATE_HELP_TEXT)
    status = forms.ChoiceField(
        choices=_get_status_choices(), initial=Event.DRAFT)
    hubs = forms.ModelMultipleChoiceField(
        queryset=Hub.objects.filter(status=Hub.PUBLISHED),
        required=False, widget=forms.CheckboxSelectMultiple)
    contact = forms.ModelChoiceField(
        queryset=Organization.active.all(), required=False)
    audiences = forms.ModelMultipleChoiceField(
        queryset=Audience.objects.all(), required=False,
        widget=forms.CheckboxSelectMultiple)

    def clean_tags(self):
        if 'tags' in self.cleaned_data:
            return output.prepare_tags(self.cleaned_data['tags'])

    class Meta:
        fields = (
            'name', 'status', 'description', 'website', 'tickets_url',
            'image', 'start_datetime', 'end_datetime', 'event_type',
            'audiences', 'audience_other', 'scope', 'address',
            'position', 'contact', 'hubs', 'tags'
        )
        model = Event


EventURLFormSet = inlineformset_factory(
    Event, EventURL, max_num=3, can_delete=False)
