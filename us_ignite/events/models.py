import watson

from django.db import models
from django.core.urlresolvers import reverse

from django_extensions.db.fields import (
    AutoSlugField, CreationDateTimeField, ModificationDateTimeField)
from geoposition.fields import GeopositionField
from taggit.managers import TaggableManager

from us_ignite.common.fields import AutoUUIDField
from us_ignite.events import managers, exporter, search


class Audience(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class EventType(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Event(models.Model):
    PUBLISHED = 1
    DRAFT = 2
    REMOVED = 3
    STATUS_CHOICES = (
        (PUBLISHED, 'Published'),
        (DRAFT, 'Draft'),
        (REMOVED, 'Removed'),
    )
    NATIONAL = 1
    REGIONAL = 2
    SCOPE_CHOICES = (
        (NATIONAL, 'National'),
        (REGIONAL, 'Regional'),
    )
    name = models.CharField(max_length=500, verbose_name=u'event name')
    slug = AutoUUIDField(unique=True, editable=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PUBLISHED)
    image = models.ImageField(upload_to="events", blank=True)
    description = models.TextField(verbose_name=u'short description')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True, null=True)
    address = models.TextField()
    contact = models.ForeignKey(
        'organizations.Organization', blank=True, null=True,
        on_delete=models.SET_NULL)
    scope = models.IntegerField(choices=SCOPE_CHOICES, default=NATIONAL)
    audiences = models.ManyToManyField('events.Audience', blank=True)
    audience_other = models.CharField(blank=True, max_length=200)
    website = models.URLField(max_length=500, blank=True)
    event_type = models.ForeignKey(
        'events.EventType', blank=True, null=True, on_delete=models.SET_NULL)
    tickets_url = models.URLField(max_length=500, blank=True)
    tags = TaggableManager(blank=True)
    hubs = models.ManyToManyField('hubs.Hub', verbose_name=u'communities')
    position = GeopositionField(blank=True)
    user = models.ForeignKey(
        'auth.User', blank=True, null=True, on_delete=models.SET_NULL)
    is_ignite = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    # managers:
    objects = models.Manager()
    published = managers.EventPublishedManager()

    class Meta:
        ordering = ('-is_featured', 'start_datetime')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event_detail', args=[self.slug])

    def is_published(self):
        return self.status == self.PUBLISHED

    def is_draft(self):
        return self.status == self.DRAFT

    def is_owner(self, user):
        return self.user == user

    def is_visible_by(self, user):
        return self.is_published() or self.is_owner(user)

    def get_google_calendar_url(self):
        return exporter.get_google_calendar_url(
            self.name, self.start_datetime, self.end_datetime,
            self.description, self.address)

    def get_ics_url(self):
        return reverse('event_detail_ics', args=[self.slug])

    def get_edit_url(self):
        return reverse('event_edit', args=[self.slug])

    def get_location_dict(self):
        return {
            'type': 'event',
            'latitude': self.position.latitude,
            'longitude': self.position.longitude,
            'name': self.name,
            'website': self.get_absolute_url(),
            'category': '',
            'image': '',
            'content': self.name,
        }


class EventURL(models.Model):
    event = models.ForeignKey('events.Event')
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=500)

    def __unicode__(self):
        return self.name

# Search:
watson.register(
    Event.published.all(),
    search.EventSearchAdapter
)
