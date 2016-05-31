from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^playlists/(?P<playlist_id>[0-9]+)/edit/$', views.edit, name='edit'),
    url(r'^playlists/(?P<playlist_id>[0-9]+)/$', views.playlist, name='playlist'),
    url(r'^new/$', views.new, name='new'),
    url(r'^today/$', views.today, name='today'),
    url(r'^summary/$', views.summary, name='summary'),
    url(r'^reports/$', views.reports, name='reports'),
    url(r'^shows/(?P<show_id>[0-9]+)/$', views.shows, name='show'),
]
