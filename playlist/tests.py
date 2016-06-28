from django.test import TestCase
from django.template import Template, Context
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from views import ShowViewSet
from django.core.urlresolvers import reverse, resolve

from session.models import Whitelist

import views


class ShowViewsetTest(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user('user', 'password', 'fake1@user.com');
    self.whitelist = Whitelist.objects.create(ip='127.0.1.1', name="test whitelist")


  def test_no_access_for_unauthenticated_unwhitelisted(self):
    """ Makes sure a non-authenticated, non-whitelisted request fails with forbidden"""
    factory = APIRequestFactory()
    url = reverse('Show-list')
    view = resolve(url).func
    request = factory.get(url)
    response = view(request)
    self.assertEqual(response.status_code, 403)

  def test_grant_access_for_unauthenticated_whitelisted(self):
    """ Makes sure a non-authenticated, but whitelisted request succeeds"""
    factory = APIRequestFactory()
    url = reverse('Show-list')
    view = resolve(url).func
    request = factory.get(url, REMOTE_ADDR="127.0.1.1")
    response = view(request)
    self.assertEqual(response.status_code, 200)

  def test_grant_access_for_authenticated(self):
    """ Makes sure an authenticated, request succeeds"""
    factory = APIRequestFactory()
    url = reverse('Show-list')
    view = resolve(url).func
    request = factory.get(url)
    force_authenticate(request, self.user)
    response = view(request)
    self.assertEqual(response.status_code, 200)


class PlaylistViewsetTest(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user('user', 'password', 'fake1@user.com');
    self.whitelist = Whitelist.objects.create(ip='127.198.1.1', name="test whitelist")


  def test_no_access_for_unauthenticated_unwhitelisted(self):
    """ Makes sure a non-authenticated, non-whitelisted request fails with forbidden"""
    factory = APIRequestFactory()
    url = reverse('Playlist-list')
    view = resolve(url).func
    request = factory.get(url)
    response = view(request)
    self.assertEqual(response.status_code, 403)

  def test_grant_access_for_unauthenticated_whitelisted(self):
    """ Makes sure a non-authenticated, but whitelisted request succeeds"""
    factory = APIRequestFactory()
    url = reverse('Playlist-list')
    view = resolve(url).func
    request = factory.get(url, REMOTE_ADDR="127.198.1.1")
    response = view(request)
    self.assertEqual(response.status_code, 200)

  def test_grant_access_for_authenticated(self):
    """ Makes sure an authenticated, request succeeds"""
    factory = APIRequestFactory()
    url = reverse('Playlist-list')
    view = resolve(url).func
    request = factory.get(url)
    force_authenticate(request, self.user)
    response = view(request)
    self.assertEqual(response.status_code, 200)
