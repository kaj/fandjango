from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^fandjango/', include('fandjango.foo.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^what/(?P<slug>[a-z0-9_]+)', 'fandjango.libris.views.refKey'),
    (r'^(?P<year>[0-9]{4})', 'fandjango.libris.views.year'),
    (r'^(?P<slug>[a-z0-9_]+)', 'fandjango.libris.views.title'),
    (r'^$', 'fandjango.libris.views.index'),
)
