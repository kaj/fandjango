from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^fandjango/', include('fandjango.foo.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^fa/(?P<slug>[0-9.]+)$', 'libris.views.refKey'),
    (r'^what/(?P<slug>[a-z0-9_]+)$', 'libris.views.refKey'),
    (r'^what/$', 'libris.views.refKeys'),
    (r'^who/(?P<slug>[a-z0-9_]+)$', 'libris.views.creator'),
    (r'^who/$', 'libris.views.creators'),
    (r'^titles$', 'libris.views.titles'),
    (r'^(?P<year>[0-9]{4})$', 'libris.views.year'),
    (r'^(?P<slug>[a-z0-9_]+)$', 'libris.views.title'),
    (r'^$', 'libris.views.index'),
)

from libris.views import redirectold
handler404 = redirectold

if settings.DEBUG:
    urlpatterns += patterns('', url('\+404', handler404))
