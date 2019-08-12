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
from session.views import UserViewSet, MigrateAndLogin
from catalogue.views import ReleaseViewSet, TrackViewSet, ArtistViewSet, CommentViewSet
from downloads import views as downloadViews
from supporters import views as supporterViews
from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title="Intranet")

router = routers.DefaultRouter()
router.register(r'releases', ReleaseViewSet, 'release')
router.register(r'tracks', TrackViewSet, 'track')
router.register(r'artists', ArtistViewSet, 'Artist')
router.register(r'comments', CommentViewSet, 'Comment')

router.register(r'shows', views.ShowViewSet, 'Show')
router.register(r'users', UserViewSet, 'user')
router.register(r'playlists', views.PlaylistViewSet, 'Playlist')
router.register(r'playlistentries', views.PlaylistEntryViewSet,
                'PlaylistEntry')

router.register(r'supporters', supporterViews.SupporterViewSet, 'Supporter')
router.register(r'transactions', supporterViews.TransactionViewSet, 'Transaction')

urlpatterns = [
    #url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^auth', MigrateAndLogin.as_view()),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^logger/', include('playlist.urls')),
    url(r'^download/([a-f0-9\-]+)', downloadViews.download),
    url(r'^swagger', schema_view)
]
