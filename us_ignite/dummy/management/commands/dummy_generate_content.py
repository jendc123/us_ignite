from datetime import timedelta
from optparse import make_option
from random import choice, shuffle

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from us_ignite.apps.models import (
    Application,
    Domain,
    Feature,
    Page,
    PageApplication,
)
from us_ignite.blog.models import BlogLink, Post
from us_ignite.challenges.models import Challenge, Entry, Question
from us_ignite.dummy import text, images, locations
from us_ignite.events.models import Event
from us_ignite.hubs.models import Hub, HubMembership, NetworkSpeed
from us_ignite.maps.models import Category, Location
from us_ignite.news.models import Article
from us_ignite.organizations.models import Organization, OrganizationMember
from us_ignite.profiles.models import Profile
from us_ignite.resources.models import Resource, ResourceType, Sector
from taggit.models import Tag


def _choice(*args):
    """Choice between the args and an empty string."""
    return choice([''] + list(args))


def _get_start_date():
    days = choice(range(-5, 50))
    return timezone.now() + timedelta(days=days)


def _create_users():
    users = ['banana', 'apple', 'orange', 'cherry', 'lemon', 'grape']
    profile_list = []
    for f in users:
        email =  '%s@us-ignite.org' % f
        user, is_new = User.objects.get_or_create(
            username=f, is_active=True, email=email)
        if is_new and choice([True, False]):
            data = {
                'quote': text.random_words(9)[:140],
                'bio': text.random_paragraphs(2),
                'position': locations.get_location(),
                'user': user,
                'name': f,
                'availability': choice(Profile.AVAILABILITY_CHOICES)[0],
            }
            profile = Profile.objects.create(**data)
            _add_tags(profile)
            profile_list.append(profile)
    return profile_list


def _get_user():
    return User.objects.all().order_by('?')[0]


def _get_url():
    return u'http://us-ignite.org'


def _get_domain():
    return Domain.objects.all().order_by('?')[0]


def _get_hub():
    return Hub.objects.filter(status=Hub.PUBLISHED).order_by('?')[0]


def _create_organization_membership(organization):
    for user in User.objects.all().order_by('?')[:3]:
        data = {
            'organization': organization,
            'user': user,
        }
        OrganizationMember.objects.create(**data)


def _create_organization():
    name = text.random_words(3)
    image_name = u'%s.png' % slugify(text.random_words(1))
    data = {
        'name': name.title(),
        'slug': slugify(name),
        'status': choice(Organization.STATUS_CHOICES)[0],
        'bio': _choice(text.random_words(30)),
        'image': images.random_image(image_name),
        'position': locations.get_location(),
        'interest_ignite': _choice(text.random_paragraphs(1)),
        'interests_other': _choice(text.random_words(5)),
        'resources_available': _choice(text.random_paragraphs(1)),
    }
    organization = Organization.objects.create(**data)
    _add_tags(organization)
    _create_organization_membership(organization)
    return organization


def _get_organization():
    return Organization.objects.all().order_by('?')[0]


def _create_app():
    image_name = images.random_image(u'%s.png' % text.random_words(1))
    data = {
        'name': text.random_words(3).title(),
        'stage': choice(Application.STAGE_CHOICES)[0],
        'status': choice(Application.STATUS_CHOICES)[0],
        'website': _get_url(),
        'summary': _choice(text.random_words(20))[:140],
        'impact_statement': text.random_words(20)[:140],
        'assistance': _choice(text.random_words(30)),
        'team_name': _choice(text.random_words(5)),
        'team_description': _choice(text.random_words(30)),
        'acknowledgments': _choice(text.random_words(30)),
        'domain': _get_domain(),
        'is_featured': choice([True, False]),
        'owner': _get_user(),
        'image': image_name,
    }
    application = Application.objects.create(**data)
    _add_tags(application)
    return application


def _create_page():
    data = {
        'name': text.random_words(3).title(),
        'status': choice(Application.STATUS_CHOICES)[0],
        'description': text.random_paragraphs(2),
    }
    page = Page.objects.create(**data)
    app_list = (Application.objects
                .filter(status=Application.PUBLISHED).order_by('?')[:10])
    for i, app in enumerate(app_list):
        PageApplication.objects.create(page=page, application=app, order=i)


def _create_hub_membership(hub):
    for user in User.objects.all().order_by('?')[:3]:
        data = {
            'hub': hub,
            'user': user,
        }
        HubMembership.objects.create(**data)


def _create_hub():
    image_name = images.random_image(u'%s.png' % text.random_words(1))
    data = {
        'name': text.random_words(3).title(),
        'contact': choice([None, _get_user()]),
        'summary': text.random_words(10),
        'connections': text.random_paragraphs(1),
        'organization': choice([None, _get_organization()]),
        'network_speed': NetworkSpeed.objects.all().order_by('?')[0],
        'is_advanced': choice([True, False]),
        'experimentation': choice(Hub.EXPERIMENTATION_CHOICES)[0],
        'estimated_passes': text.random_words(10),
        'description': text.random_paragraphs(3),
        'image': image_name,
        'website': _get_url(),
        'status': choice(Hub.STATUS_CHOICES)[0],
        'is_featured': choice([True, False]),
        'position': locations.get_location(),
    }
    hub = Hub.objects.create(**data)
    _create_hub_membership(hub)
    _add_tags(hub)
    _add_features(hub)
    _add_applications(hub)
    return hub


def _create_event():
    start_date = _get_start_date()
    end_date = start_date + timedelta(hours=5)
    data = {
        'name': text.random_words(5),
        'status': choice(Event.STATUS_CHOICES)[0],
        'image': images.random_image(u'%s.png' % text.random_words(1)),
        'start_datetime': start_date,
        'end_datetime': choice([None, end_date]),
        'address': text.random_words(7),
        'description': text.random_paragraphs(2),
        'is_featured': choice([True, False]),
        'user': _get_user(),
        'position': locations.get_location(),
    }
    event = Event.objects.create(**data)
    _add_tags(event)
    for i in range(0, 3):
        event.hubs.add(_get_hub())
    return event


def _create_challenge():
    start_date = _get_start_date()
    end_date = start_date + timedelta(days=15)
    data = {
        'name': text.random_words(5).title(),
        'status': choice(Challenge.STATUS_CHOICES)[0],
        'start_datetime': start_date,
        'end_datetime': end_date,
        'url': _get_url(),
        'is_external': choice([True, False]),
        'summary': text.random_paragraphs(1),
        'description': text.random_paragraphs(3),
        'image': images.random_image(u'%s.png' % text.random_words(1)),
        'user': _get_user(),
    }
    challenge = Challenge.objects.create(**data)
    for i in range(0, 10):
        _create_question(challenge, i)
    _create_entries(challenge)
    return challenge


def _create_question(challenge, order=0):
    data = {
        'challenge': challenge,
        'question': u'%s?' % text.random_words(7),
        'is_required': choice([True, False]),
        'order': order,
    }
    return Question.objects.create(**data)


def _create_entries(challenge):
    apps = list(Application.objects.all().order_by('?'))
    entry_list = []
    for i in range(0, choice(range(1, 10))):
        data = {
            'challenge': challenge,
            'application': apps.pop(),
            'status': choice(Entry.STATUS_CHOICES)[0],
            'notes': _choice(text.random_words(10)),
        }
        entry = Entry.objects.create(**data)
        entry_list.append(entry)
    return entry_list


def _get_resource_type():
    return ResourceType.objects.all().order_by('?')[0]


def _get_sector():
    return Sector.objects.all().order_by('?')[0]


def _create_resource():
    name = text.random_words(4)
    data = {
        'name': name.title(),
        'slug': slugify(name),
        'status': choice(Resource.STATUS_CHOICES)[0],
        'description': text.random_paragraphs(1),
        'contact': _get_user(),
        'author': _choice(text.random_words(10)),
        'resource_date': choice([_get_start_date(), None]),
        'url': _get_url(),
        'is_featured': choice([True, False]),
        'image': images.random_image(u'%s.png' % text.random_words(1)),
        'resource_type': _get_resource_type(),
        'sector': _get_sector(),
    }
    resource = Resource.objects.create(**data)
    _add_tags(resource)
    return resource


def _feature_posts():
    for post in Post.objects.all().order_by('?')[:5]:
        post.is_featured = True
        post.save()
        _add_tags(post)


def _create_article():
    data = {
        'name': text.random_words(7).title(),
        'status': choice(Article.STATUS_CHOICES)[0],
        'url': _get_url(),
        'is_featured': choice([True, False]),
    }
    return Article.objects.create(**data)


def _create_blog_link():
    data = {
        'name': text.random_words(6).title(),
        'url': _get_url(),
    }
    return BlogLink.objects.create(**data)


def _create_location_category():
    name = text.random_words(2).title()
    data = {
        'name': name,
        'slug': slugify(name),
    }
    return Category.objects.create(**data)


def _get_location_category():
    return Category.objects.all().order_by('?')[0]


def _create_location():
    data = {
        'name': text.random_words(4).title(),
        'website': _get_url(),
        'status': choice(Location.STATUS_CHOICES)[0],
        'position': locations.get_location(),
        'category': _get_location_category(),
    }
    return Location.objects.create(**data)


def _get_tags(total=5):
    tags = ['gigabit', 'healthcare', 'education', 'energy']
    tags += [slugify(w) for w in text.random_words(total).split()]
    shuffle(tags)
    return tags[:total]


def _add_tags(item):
    tags = _get_tags()
    item.tags.add(*tags)
    return tags


def _feature_tags():
    Tag.objects.all().update(is_featured=True)


def _add_features(item, total=3):
    features = Feature.objects.all().order_by('?')[:total]
    return [item.features.add(f) for f in features]


def _add_applications(item, total=3):
    apps = Application.objects.all().order_by('?')[:total]
    return [item.applications.add(a) for a in apps]


def _load_fixtures():
    """Loads initial fixtures"""
    call_command('app_load_fixtures')
    call_command('awards_load_fixtures')
    call_command('common_load_fixtures')
    call_command('snippets_load_fixtures')
    call_command('events_load_fixtures')
    call_command('resources_load_fixtures')
    call_command('hubs_load_fixtures')
    call_command('sections_load_fixtures')
    call_command('blog_import')


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '--noinput',
            action='store_true',
            dest='noinput',
            default=False,
            help='Does not ask for any user input.'),
    )
    def handle(self, *args, **options):
        if not options['noinput']:
            message = ('This command will IRREVERSIBLE poison the existing '
                       'database by adding dummy content and images. '
                       'Proceed? [y/N] ')
            response = raw_input(message)
            if not response or not response == 'y':
                print 'Phew, aborted!'
                exit(0)
        print u'Loading initial fixtures.'
        _load_fixtures()
        print u'Featuring Posts'
        _feature_posts()
        print u'Adding users.'
        _create_users()
        print u'Adding organizations.'
        for i in range(30):
            _create_organization()
        print u'Adding applications.'
        for i in range(40):
            _create_app()
        print u'Adding app pages.'
        for i in range(10):
            _create_page()
        print u'Adding hubs.'
        for i in range(40):
            _create_hub()
        print u'Adding events.'
        for i in range(30):
            _create_event()
        print u'Adding challenges.'
        for i in range(30):
            _create_challenge()
        print u'Adding resources.'
        for i in range(30):
            _create_resource()
        print u'Adding articles.'
        for i in range(30):
            _create_article()
        print u'Adding blog links.'
        for i in range(15):
            _create_blog_link()
        print u'Adding location categories.'
        for i in range(6):
            _create_location_category()
        print u'Adding locations.'
        for i in range(50):
            _create_location()
        print u'Featuring tags.'
        _feature_tags()
        print u'Done.'
