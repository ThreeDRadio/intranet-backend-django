from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.viewsets import ModelViewSet

import permissions

from models import Whitelist

class IsStaffOrTargetUserTest(TestCase):
  def setUp(self):
    self.user = User.objects.create_user('user', 'password', 'fake@user.com');
    self.admin = User.objects.create_user('admin', 'password', 'fake@user.com');
    self.admin.is_staff=True
    self.admin.save()


  def test_has_permission_no_auth(self):
    """View level returns true if the request is a retrieve, otherwise false"""
    factory = APIRequestFactory()
    request = factory.get('api/users');
    permission = permissions.IsStaffOrTargetUser()

    view = ModelViewSet();
    view.action = 'retrieve'
    self.assertEqual(permission.has_permission(request, view), True)

    view.action = 'list'
    self.assertEqual(permission.has_permission(request, view), False)

    view.action = 'create'
    self.assertEqual(permission.has_permission(request, view), False)

    view.action = 'update'
    self.assertEqual(permission.has_permission(request, view), False)
    view.action = 'partial_update'
    self.assertEqual(permission.has_permission(request, view), False)
    view.action = 'destroy'
    self.assertEqual(permission.has_permission(request, view), False)

  def test_has_permission_regular_user(self):
    """View level returns true if the request is a retrieve, otherwise false"""
    factory = APIRequestFactory()
    request = factory.get('api/users');
    permission = permissions.IsStaffOrTargetUser()
    force_authenticate(request, self.user)

    view = ModelViewSet();
    view.action = 'retrieve'
    self.assertEqual(permission.has_permission(request, view), True)

    view.action = 'list'
    self.assertEqual(permission.has_permission(request, view), False)

    view.action = 'create'
    self.assertEqual(permission.has_permission(request, view), False)

    view.action = 'update'
    self.assertEqual(permission.has_permission(request, view), False)
    view.action = 'partial_update'
    self.assertEqual(permission.has_permission(request, view), False)
    view.action = 'destroy'
    self.assertEqual(permission.has_permission(request, view), False)

  def test_has_permission_admin_user(self):
    """View level returns true if the user is staff """
    factory = APIRequestFactory()
    request = factory.get('api/users');
    request.user = self.admin
    permission = permissions.IsStaffOrTargetUser()
    force_authenticate(request, self.admin)

    view = ModelViewSet();
    view.action = 'retrieve'
    self.assertEqual(permission.has_permission(request, view), True)

    view.action = 'list'
    self.assertEqual(permission.has_permission(request, view), True)

    view.action = 'create'
    self.assertEqual(permission.has_permission(request, view), True)

    view.action = 'update'
    self.assertEqual(permission.has_permission(request, view), True)
    view.action = 'partial_update'
    self.assertEqual(permission.has_permission(request, view), True)
    view.action = 'destroy'
    self.assertEqual(permission.has_permission(request, view), True)

  def test_has_object_permission_admin_on_admin(self):
    """ Makes sure an admin user has permissions to access themselves"""
    factory = APIRequestFactory()
    request = factory.get('api/users');
    request.user = self.admin
    permission = permissions.IsStaffOrTargetUser()
    view = ModelViewSet();
    view.action = 'retrieve'
    self.assertEqual(permission.has_object_permission(request, view, self.admin), True)

  def test_has_object_permission_admin_on_user(self):
    """ Makes sure an admin user has permissions to access another user"""
    factory = APIRequestFactory()
    request = factory.get('api/users');
    request.user = self.admin
    permission = permissions.IsStaffOrTargetUser()
    view = ModelViewSet();
    view.action = 'retrieve'
    self.assertEqual(permission.has_object_permission(request, view, self.user), True)

  def test_has_object_permission_user_on_user(self):
    """ Makes sure a regular user has permissions to access themselves"""
    factory = APIRequestFactory()
    request = factory.get('api/users');
    request.user = self.user
    permission = permissions.IsStaffOrTargetUser()
    view = ModelViewSet();
    view.action = 'retrieve'
    self.assertEqual(permission.has_object_permission(request, view, self.user), True)

  def test_has_object_permission_user_on_admin(self):
    """ Makes sure a regular user cannot access other users"""
    factory = APIRequestFactory()
    request = factory.get('api/users');
    request.user = self.user
    permission = permissions.IsStaffOrTargetUser()
    view = ModelViewSet();
    view.action = 'retrieve'
    self.assertEqual(permission.has_object_permission(request, view, self.admin), False)



class IsAuthenticatedOrWhitelistTest(TestCase):
  def setUp(self):
    self.user = User.objects.create_user('user', 'password', 'fake@user.com');
    self.whitelist = Whitelist.objects.create(ip='127.0.0.1', name= 'Localhost')


  def test_unauthenticated_not_whitelisted(self):
    """ An unauthenticated, un-whitelisted IP address should not be granted permission"""
    factory = APIRequestFactory()
    request = factory.get('api/users');
    request.META['REMOTE_ADDR'] = '255.255.255.0'
    request.user = False
    permission = permissions.IsAuthenticatedOrWhitelist()
    view = ModelViewSet();
    view.action = 'retrieve'
    self.assertEqual(permission.has_permission(request, view), False)

  def test_unauthenticated_but_whitelisted(self):
    """ An unauthenticated, whitelisted IP address should be granted permission"""
    factory = APIRequestFactory()
    request = factory.get('api/users');
    request.user = False
    permission = permissions.IsAuthenticatedOrWhitelist()
    view = ModelViewSet();
    view.action = 'retrieve'
    self.assertEqual(permission.has_permission(request, view), True)

  def test_authenticated_not_whitelisted(self):
    """ An authenticated, un-whitelisted IP address should be granted permission"""
    factory = APIRequestFactory()
    request = factory.get('api/users');
    request.META['REMOTE_ADDR'] = '255.255.255.0'
    request.user = self.user 
    permission = permissions.IsAuthenticatedOrWhitelist()
    view = ModelViewSet();
    view.action = 'retrieve'
    self.assertEqual(permission.has_permission(request, view), True)

  def test_authenticated_whitelisted(self):
    """ An authenticated, un-whitelisted IP address should be granted permission"""
    factory = APIRequestFactory()
    request = factory.get('api/users');
    request.user = self.user 
    permission = permissions.IsAuthenticatedOrWhitelist()
    view = ModelViewSet();
    view.action = 'retrieve'
    self.assertEqual(permission.has_permission(request, view), True)
