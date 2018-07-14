from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from views import UserViewSet, MigrateAndLogin
from django.core.urlresolvers import reverse, resolve
from hashlib import md5

from models import OldPassword


class MigrateAndLoginTest(APITestCase):
  def setUp(self):
    self.newUser = User.objects.create_user('newUser', 'fake1@gmail.com', 'pass1')
    self.newUser.save()
    self.oldUser = User.objects.create_user('oldUser')
    self.oldUser.save()
    OldPassword.objects.create(user=self.oldUser, password=md5("pass2").hexdigest())

  def test_getOldPassword(self):
    """ Makes sure we can get an old password from a username"""
    view = MigrateAndLogin()
    oldPass = view.getOldPassword('oldUser')
    self.assertEqual(oldPass.user, self.oldUser)

    self.assertEqual(view.getOldPassword('newuser'), None)

  def test_empty_post_request_returns_errors(self):
    """ An empty post request should return a 400 error code with username and password errors"""
    factory = APIRequestFactory()
    request = factory.post('/api-token-auth')
    view = MigrateAndLogin()
    response = view.post(request)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.data['username'], 'This field is required')
    self.assertEqual(response.data['password'], 'This field is required')


  def test_no_password_returns_error(self):
    """ An empty post request should return a 400 error code with password error"""
    factory = APIRequestFactory()
    request = factory.post('/api-token-auth', {'username': 'mmarner'})
    view = MigrateAndLogin()
    response = view.post(request)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.data['password'], 'This field is required')
    self.assertEqual('username' in response.data, False)

  def test_no_username_returns_error(self):
    """ An post request with no username should return a 400 error code with username error"""
    factory = APIRequestFactory()
    request = factory.post('/api-token-auth', {'password': 'mmarner'})
    view = MigrateAndLogin()
    response = view.post(request)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.data['username'], 'This field is required')
    self.assertEqual('password' in response.data, False)


  def test_user_with_new_password_authenticates(self):
    """ A user with a valid username/password gets a token """
    factory = APIRequestFactory()
    request = factory.post('/api-token-auth', {'username': 'newUser', 'password': 'pass1'})
    view = MigrateAndLogin.as_view()
    response = view(request)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['token'], self.newUser.auth_token.key)

  def test_user_with_old_password_authenticates_and_migrates(self):
    """ A user with a valid username/password gets a token """
    factory = APIRequestFactory()
    request = factory.post('/api-token-auth', {'username': 'oldUser', 'password': 'pass2'})
    view = MigrateAndLogin.as_view()
    response = view(request)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['token'], self.oldUser.auth_token.key)

    # Old password should have been deleted
    self.assertEqual(OldPassword.objects.filter(user=self.oldUser).exists(), False)

    # new password should exist in user table
    user = User.objects.get(username='oldUser')
    self.assertEqual(user.check_password('pass2'), True)
