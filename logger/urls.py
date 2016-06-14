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
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from playlist import views
from session.views import SessionView, UserViewSet

router = routers.DefaultRouter()
router.register(r'releases', views.ReleaseViewSet)
router.register(r'tracks', views.TrackViewSet)
router.register(r'artists', views.ArtistViewSet, 'Artist')
router.register(r'shows', views.ShowViewSet, 'Show')
router.register(r'users', UserViewSet, 'User')
router.register(r'playlists', views.PlaylistViewSet, 'Playlist')
router.register(r'playlistentries', views.PlaylistEntryViewSet, 'PlaylistEntry')

urlpatterns = [
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^logger/', include('playlist.urls')),
]
