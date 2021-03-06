from mock import patch
from nose.tools import eq_, ok_

from django.contrib.auth.models import User
from django.test import TestCase

from us_ignite.apps.models import Application
from us_ignite.apps.tests.fixtures import get_application
from us_ignite.common.tests import utils
from us_ignite.hubs.models import (Hub, HubActivity, HubMembership, HubRequest,
                                   HubAppMembership)
from us_ignite.hubs.tests import fixtures
from us_ignite.profiles.tests.fixtures import get_user


class TestHubRequestModel(TestCase):

    def tearDown(self):
        for model in [HubRequest, User]:
            model.objects.all().delete()

    def test_model_can_be_created_successfully(self):
        user = get_user('us-ignite')
        data = {
            'name': 'Local Community',
            'description': 'Gigabit local community',
            'user': user,
        }
        instance = HubRequest.objects.create(**data)
        ok_(instance.id)
        eq_(instance.name, 'Local Community')
        eq_(instance.user, user)
        eq_(instance.summary, '')
        eq_(instance.description, 'Gigabit local community')
        eq_(instance.website, '')
        ok_(instance.created)
        ok_(instance.modified)
        eq_(instance.hub, None)

    def test_admin_url(self):
        user = get_user('us-ignite')
        instance = fixtures.get_hub_request(user=user)
        eq_(instance.get_admin_url(),
            '/admin/hubs/hubrequest/%s/' % instance.id)

    def test_is_approved(self):
        user = get_user('us-ignite')
        instance = fixtures.get_hub_request(
            user=user, status=HubRequest.APPROVED)
        eq_(instance.is_approved(), True)

    def test_is_rejected(self):
        user = get_user('us-ignite')
        instance = fixtures.get_hub_request(
            user=user, status=HubRequest.REJECTED)
        eq_(instance.is_rejected(), True)

    def test_is_removed(self):
        user = get_user('us-ignite')
        instance = fixtures.get_hub_request(
            user=user, status=HubRequest.REMOVED)
        eq_(instance.is_removed(), True)

    def test_is_pending(self):
        user = get_user('us-ignite')
        instance = fixtures.get_hub_request(
            user=user, status=HubRequest.PENDING)
        eq_(instance.is_pending(), True)
        eq_(instance.hub, None)


class TestHubModel(TestCase):

    def tearDown(self):
        for model in [Hub, User]:
            model.objects.all().delete()

    def test_model_can_be_created_successfully(self):
        data = {
            'name': 'Local Community',
            'description': 'Gigabit local community',
        }
        instance = Hub.objects.create(**data)
        ok_(instance.id)
        eq_(instance.name, 'Local Community')
        eq_(instance.slug, 'local-community')
        eq_(instance.summary, '')
        eq_(instance.description, 'Gigabit local community')
        eq_(instance.connections, '')
        eq_(instance.contact, None)
        eq_(instance.organization, None)
        eq_(instance.network_speed, None)
        eq_(instance.is_advanced, False)
        eq_(instance.experimentation, Hub.MEDIUM)
        eq_(instance.estimated_passes, '')
        eq_(instance.image, '')
        eq_(instance.website, '')
        eq_(instance.notes, '')
        eq_(instance.status, Hub.DRAFT)
        eq_(list(instance.applications.all()), [])
        eq_(list(instance.features.all()), [])
        eq_(list(instance.tags.all()), [])
        ok_(instance.created)
        ok_(instance.modified)
        ok_(instance.position)

    def test_is_contact(self):
        contact = get_user('contact')
        instance = fixtures.get_hub(contact=contact)
        eq_(instance.is_contact(contact), True)

    def test_is_published(self):
        contact = get_user('contact')
        instance = fixtures.get_hub(contact=contact, status=Hub.PUBLISHED)
        eq_(instance.is_published(), True)

    def test_is_draft(self):
        contact = get_user('contact')
        instance = fixtures.get_hub(contact=contact, status=Hub.DRAFT)
        eq_(instance.is_draft(), True)

    def test_published_hub_is_visible(self):
        instance = fixtures.get_hub(status=Hub.PUBLISHED)
        eq_(instance.is_visible_by(utils.get_anon_mock()), True)

    def test_unpublished_hub_is_visible_to_contact(self):
        contact = get_user('contact')
        instance = fixtures.get_hub(contact=contact, status=Hub.DRAFT)
        eq_(instance.is_visible_by(contact), True)

    def test_get_absolute_url(self):
        contact = get_user('contact')
        instance = fixtures.get_hub(contact=contact)
        eq_(instance.get_absolute_url(), '/hub/%s/' % instance.slug)

    def test_get_membership_url(self):
        contact = get_user('contact')
        instance = fixtures.get_hub(contact=contact)
        eq_(instance.get_membership_url(), '/hub/%s/membership/' % instance.slug)

    @patch('us_ignite.hubs.models.HubActivity.objects.create')
    def test_record_activity_is_successful(self, mock_create):
        contact = get_user('contact')
        instance = fixtures.get_hub(contact=contact)
        instance.record_activity('Hello')
        mock_create.assert_called_once_with(hub=instance, name='Hello')


class TestHubActivityModel(TestCase):

    def tearDown(self):
        for model in [Hub]:
            model.objects.all().delete()

    def create_hub_activity_is_successful(self):
        hub = fixtures.create_hub('Gigabit hub')
        data = {
            'hub': hub,
            'title': 'New app added!',
        }
        instance = HubActivity.objects.craete(**data)
        ok_(instance.id)
        eq_(instance.hub, hub)
        eq_(instance.title, 'New app added!')
        eq_(instance.description, '')
        eq_(instance.url, '')
        eq_(instance.user, None)
        ok_(instance.created)
        ok_(instance.modified)


class TestHubMembershipModel(TestCase):

    def tearDown(self):
        for model in [Hub, User]:
            model.objects.all().delete()

    def test_create_membership(self):
        user = get_user('member')
        hub = fixtures.get_hub(status=Hub.PUBLISHED)
        data = {
            'hub': hub,
            'user': user,
        }
        instance = HubMembership.objects.create(**data)
        ok_(instance.id)
        eq_(instance.hub, hub)
        eq_(instance.user, user)
        ok_(instance.created)


class TestHubAppMembershipModel(TestCase):

    def tearDown(self):
        for model in [Hub, Application, User]:
            model.objects.all().delete()

    def test_membership_is_create_successful(self):
        user = get_user('owner')
        hub = fixtures.get_hub(name='Gigabit hub')
        app = get_application(owner=user)
        data = {
            'hub': hub,
            'application': app,
        }
        instance = HubAppMembership.objects.create(**data)
        ok_(instance.id)
        eq_(instance.hub, hub)
        eq_(instance.application, app)
        eq_(instance.is_featured, False)
        ok_(instance.created)
