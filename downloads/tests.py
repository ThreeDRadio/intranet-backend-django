from django.test import TestCase, override_settings
from django.shortcuts import Http404
import os
from models import DownloadLink
import views
from datetime import timedelta
from django.test import RequestFactory

# Create your tests here.

@override_settings(DOWNLOAD_BASE_PATH=os.getcwd())
class DownloadLinkModelTest(TestCase):

  def test_can_create_links(self):
    """ Can create DownloadLink objects """
    link = DownloadLink(name="Download Name")
    self.assertEqual(link.name, "Download Name")

  def test_links_have_path(self):
    """ Make sure the link has a path that is set properly."""
    link = DownloadLink(path="/home/not/real")
    self.assertEqual(link.path, "/home/not/real")

  @override_settings(DOWNLOAD_LIFETIME=60)
  def test_expiry_in_future(self):
    """ Make sure the expiry is in the future based on settings"""
    link = DownloadLink()
    link.save()
    self.assertEqual(link.getExpiry(), link.createdAt + timedelta(seconds=60))

  @override_settings(DOWNLOAD_LIFETIME=60)
  def test_isCurrent_good(self):
    """ Makes sure new links are current"""
    link = DownloadLink()
    link.save()
    self.assertTrue(link.isCurrent())

    link.createdAt = link.createdAt - timedelta(seconds=61)
    self.assertFalse(link.isCurrent())

  @override_settings(DOWNLOAD_LIFETIME=60)
  def test_isCurrent_stale(self):
    """ Makes sure old links are expired"""
    link = DownloadLink()
    link.save()
    link.createdAt = link.createdAt - timedelta(seconds=61)
    self.assertFalse(link.isCurrent())


  def test_download_view_invalid_url(self):
    """ Download view should return a 404 if link doesn't exist"""
    factory = RequestFactory()
    request = factory.get('/downloads');
    error = False
    try:
      response = views.download(request, 'fake_id');
    except: 
      error = True

    self.assertTrue(error)

  @override_settings(DOWNLOAD_LIFETIME=60)
  def test_download_view_valid(self):
    """ Download should return the xfile header for a good link"""
    link = DownloadLink(path='/home/blah/file')
    link.save()
    factory = RequestFactory()
    request = factory.get('/downloads');
    error = False
    response = views.download(request, link.id);
    self.assertEqual(response['X-SendFile'], link.path)


  @override_settings(DOWNLOAD_LIFETIME=60)
  def test_download_view_expired(self):
    """ Download should 404 if the link has expired"""
    link = DownloadLink()
    link.save()
    link.createdAt = link.createdAt - timedelta(seconds=61)
    link.save()

    factory = RequestFactory()
    request = factory.get('/downloads');

    error = False
    try:
      response = views.download(request, link.id);
    except: 
      error = True

    self.assertTrue(error)
