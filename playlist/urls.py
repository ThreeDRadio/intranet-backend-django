from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^summary/$", views.summary, name="summary"),
    re_path(r"^playlists/(?P<playlist_id>[0-9]+)/$", views.playlist, name="playlist"),
]
