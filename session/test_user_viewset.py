from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from views import UserViewSet
from django.core.urlresolvers import reverse, resolve


class UserViewSetTest(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user('user', 'password', 'fake1@user.com');
    self.admin = User.objects.create_user('admin', 'password', 'fake2@user.com');
    self.admin.is_staff=True
    self.admin.save()

  def test_get_me_no_user(self):
    """Makes sure that accessing /users/me unauthenticated returns 400"""
    factory = APIRequestFactory()
    url = reverse('user-detail', args=('me',))
    view = resolve(url).func
    request = factory.get(url)
    response = view(request, pk='me')
    self.assertEqual(response.status_code, 400)

  def test_get_me_normal_user(self):
    """Makes sure that accessing /users/me returns the correct user for normal user"""
    factory = APIRequestFactory()
    url = reverse('user-detail', args=('me',))
    view = resolve(url).func
    request = factory.get(url)
    force_authenticate(request, self.user)
    response = view(request, pk='me')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['id'], self.user.id)

  def test_get_me_admin_user(self):
    """Makes sure that accessing /users/me returns the correct user for staff user"""
    factory = APIRequestFactory()
    url = reverse('user-detail', args=('me',))
    view = resolve(url).func
    request = factory.get(url)
    force_authenticate(request, self.admin)
    response = view(request, pk='me')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['id'], self.admin.id)


  def test_admin_get_other_user(self):
    """Makes sure that staff can access other users"""
    factory = APIRequestFactory()
    url = reverse('user-detail', args=(self.user.pk,))
    view = resolve(url).func
    request = factory.get(url)
    force_authenticate(request, self.admin)
    response = view(request, pk=self.user.pk)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['id'], self.user.id)

  def test_admin_get_self(self):
    """Makes sure that staff can access other users"""
    factory = APIRequestFactory()
    url = reverse('user-detail', args=(self.admin.pk,))
    view = resolve(url).func
    request = factory.get(url)
    force_authenticate(request, self.admin)
    response = view(request, pk=self.admin.pk)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['id'], self.admin.id)

  def test_user_get_self(self):
    """Makes sure that regular users can access themselves"""
    factory = APIRequestFactory()
    url = reverse('user-detail', args=(self.user.pk,))
    view = resolve(url).func
    request = factory.get(url)
    force_authenticate(request, self.user)
    response = view(request, pk=self.user.pk)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['id'], self.user.id)

  def test_user_get_other(self):
    """Makes sure that regular users cannot access other users"""
    factory = APIRequestFactory()
    url = reverse('user-detail', args=(self.admin.pk,))
    view = resolve(url).func
    request = factory.get(url)
    force_authenticate(request, self.user)
    response = view(request, pk=self.admin.pk)
    self.assertEqual(response.status_code, 403)
