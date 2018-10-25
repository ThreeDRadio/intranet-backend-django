from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^summary/$', views.summary, name='summary'),
    url(r'^playlists/(?P<playlist_id>[0-9]+)/$', views.playlist, name='playlist'),
    url(r'^reports/$', views.reports, name='reports'),
]
