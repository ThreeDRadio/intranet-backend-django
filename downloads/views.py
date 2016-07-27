from django.shortcuts import get_object_or_404, Http404
from models import DownloadLink
from django.http import HttpResponse


def download(request, linkID):
  """ Returns a file through Apache's X-Sendfile header, if the link is valid"""
  try:
    link = get_object_or_404(DownloadLink, pk=linkID)
  except:
    raise Http404("Invalid download link: " + linkID)

  if link.isCurrent():
    response = HttpResponse()
    response['X-Sendfile'] = link.path
    return response
  else:
    raise Http404("Download link expired: " + linkID)

