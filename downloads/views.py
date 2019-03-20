from django.shortcuts import get_object_or_404, Http404
from .models import DownloadLink
from django.http import HttpResponse
from django.views.static import serve;
from django.conf import settings
import os

def download(request, linkID):
  """ Returns a file through Apache's X-Sendfile header, if the link is valid"""
  try:
    link = get_object_or_404(DownloadLink, pk=linkID)
  except:
    raise Http404("Invalid download link: " + linkID)

  if link.isCurrent():
    if hasattr(settings, 'DOWNLOAD_X_SENDFILE') and settings.DOWNLOAD_X_SENDFILE:
      return serve(request, os.path.basename(link.path), os.path.dirname(link.path))
    else:
      response = HttpResponse()
      response['X-Sendfile'] = link.path
      response['X-Accel-Redirect'] = link.path + ';'
      return response
  else:
    raise Http404("Download link expired: " + linkID)

