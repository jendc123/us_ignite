from django.conf.urls import patterns, url


urlpatterns = patterns(
    'us_ignite.search.views',
    url(r'^$', 'search', name='search'),
    url(r'^apps/$', 'search_apps', name='search_apps'),
    url(r'^events/$', 'search_events', name='search_events'),
    url(r'^hubs/$', 'search_hubs', name='search_hubs'),
    url(r'^orgs/$', 'search_organizations', name='search_organizations'),
    url(r'^resources/$', 'search_resources', name='search_resources'),
    url(r'^tags.json$', 'tag_list', name='tag_list'),
)
