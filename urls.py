from django.conf import settings
from django.conf.urls import include, url
from libris import views

urlpatterns = [
    url(r'^fa/(?P<slug>[0-9.]+)$', views.refKey),
    url(r'^what/(?P<slug>[a-z0-9_]+)$', views.refKey),
    url(r'^what/$', views.refKeys),
    url(r'^who/(?P<slug>[a-z0-9_]+)$', views.creator),
    url(r'^who/$', views.creators),
    url(r'^titles$', views.titles),
    url(r'^ac$', views.autocomplete),
    url(r'^search$', views.search),
    url(r'^(?P<year>[0-9]{4})$', views.year),
    url(r'^(?P<strips>(sun|week))days-(?P<slug>[a-z0-9_]+)$', views.title),
    url(r'^(?P<slug>[a-z0-9_]+)$', views.title),
    url(r'^$', views.index),

    url(r'^robots\.txt$', views.robots),
]

handler404 = views.redirectold

if settings.DEBUG:
    urlpatterns += [url('\+404', handler404)]
