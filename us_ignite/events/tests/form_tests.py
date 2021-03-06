from nose.tools import eq_

from django.test import TestCase

from us_ignite.events import forms


class TestEventForm(TestCase):

    def test_fields_listed_are_not_sensitive(self):
        form = forms.EventForm()
        eq_(sorted(form.fields.keys()),
            sorted(['audiences', 'contact', 'description', 'end_datetime',
                    'hubs', 'image', 'name', 'position', 'scope',
                    'start_datetime', 'status', 'tags', 'tickets_url',
                    'address', 'website', 'audience_other', 'event_type'])
        )

    def test_empty_payload_fails(self):
        form = forms.EventForm({})
        eq_(form.is_valid(), False)

    def test_valid_payload_is_successful(self):
        data = {
            'name': 'Gigabit community',
            'status': 1,
            'description': 'Gigabit meetup',
            'start_datetime': '2013-12-14 14:30:59',
            'scope': 1,
            'address': 'London UK',
        }
        form = forms.EventForm(data)
        eq_(form.is_valid(), True)
