from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from libris import views

admin.autodiscover()

urlpatterns = [
    # Example:
    # (r'^fandjango/', include('fandjango.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^fa/(?P<slug>[0-9.]+)$', views.refKey),
    url(r'^what/(?P<slug>[a-z0-9_]+)$', views.refKey),
    url(r'^what/$', views.refKeys),
    url(r'^who/(?P<slug>[a-z0-9_]+)$', views.creator),
    url(r'^who/$', views.creators),
    url(r'^titles$', views.titles),
    url(r'^(?P<year>[0-9]{4})$', views.year),
    url(r'^(?P<strips>(sun|week))days-(?P<slug>[a-z0-9_]+)$', views.title),
    url(r'^(?P<slug>[a-z0-9_]+)$', views.title),
    url(r'^$', views.index),

    url(r'^robots\.txt$', views.robots),
]

from libris.views import redirectold
handler404 = redirectold

if settings.DEBUG:
    urlpatterns += [url('\+404', handler404)]
