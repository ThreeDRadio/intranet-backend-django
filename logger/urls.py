"""logger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf.urls import include
from django.contrib import admin
from django.urls import re_path
from rest_framework import routers

from catalogue.views import ArtistViewSet, CommentViewSet, ReleaseViewSet, TrackViewSet
from downloads import views as downloadViews
from playlist import views
from session.views import MigrateAndLogin, UserViewSet

router = routers.DefaultRouter()
router.register(r"releases", ReleaseViewSet, "release")
router.register(r"tracks", TrackViewSet, "track")
router.register(r"artists", ArtistViewSet, "Artist")
router.register(r"comments", CommentViewSet, "Comment")

router.register(r"shows", views.ShowViewSet, "Show")
router.register(r"users", UserViewSet, "user")
router.register(r"playlists", views.PlaylistViewSet, "Playlist")
router.register(r"playlistentries", views.PlaylistEntryViewSet, "PlaylistEntry")

urlpatterns = [
    # url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
    re_path(r"^auth", MigrateAndLogin.as_view()),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^api/", include(router.urls)),
    re_path(r"^logger/", include("playlist.urls")),
    re_path(r"^download/([a-f0-9\-]+)", downloadViews.download),
    # re_path(r"^swagger", schema_view),
]
