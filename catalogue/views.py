from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.forms.models import modelformset_factory
from django.contrib import messages
import django_filters
from rest_framework import filters
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import unicodecsv as csv
from datetime import date
from django.db.models import Count
from django.shortcuts import render
from django.conf import settings

from .models import Release, Track
from .serializers import ReleaseSerializer, TrackSerializer, CommentSerializer
from downloads.models import DownloadLink
from session.permissions import IsAuthenticatedOrWhitelist

# Create your views here.
class ArtistViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticatedOrWhitelist,)
    filter_backends = (filters.SearchFilter, )
    search_fields = ('artist', )

    def list(self, request):
        searchParam = self.request.query_params.get('term')
        if searchParam is None:
            artists = [
                release.artist
                for release in Release.objects.distinct('artist').order_by(
                    'artist')
            ]
        else:
            artists = [
                release.artist
                for release in Release.objects.distinct('artist').filter(
                    artist__icontains=searchParam).order_by('artist')
            ]

        return Response(artists)


class ReleaseFilter(django_filters.FilterSet):
  min_arrival = django_filters.DateFilter(name="arrivaldate", lookup_expr="gte")
  artist = django_filters.CharFilter(name="artist", lookup_expr="icontains")
  track  = django_filters.CharFilter(name="tracks__tracktitle", lookup_expr="icontains")
  country = django_filters.CharFilter(name="cpa", lookup_expr="icontains")
  release = django_filters.CharFilter(name="title", lookup_expr="icontains")
  

  class Meta:
    model = Release
    fields = [
      'arrivaldate', 'artist', 'tracks__tracktitle', 'year', 'country',
      'title', 'local', 'demo', 'compilation', 'female'
    ]


class ReleaseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrWhitelist,)
    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer
    filter_backends = (filters.OrderingFilter, filters.SearchFilter,
                       django_filters.rest_framework.DjangoFilterBackend)
    search_fields = ('artist', 'title', 'tracks__tracktitle')
    ordering_fields = ('arrivaldate', 'artist', 'title')
    filter_class = ReleaseFilter

    @detail_route()
    def tracks(self, request, pk=None):
        release = self.get_object()
        serializer = TrackSerializer(
            release.tracks.all().order_by('tracknum'),
            context={'request': request},
            many=True)
        return Response(serializer.data)

    @detail_route()
    def comments(self, request, pk=None):
        release = self.get_object()
        serializer = CommentSerializer(
            release.comments.all().order_by('pk'),
            context={'request': request},
            many=True)
        return Response(serializer.data)


class TrackFilter(django_filters.FilterSet):
    artist = django_filters.CharFilter(name="album__artist", lookup_expr='icontains')
    track = django_filters.CharFilter(name="tracktitle", lookup_expr='icontains')

    class Meta:
        model = Track
        fields = ['track', 'artist']


class TrackViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrWhitelist,)
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    filter_class = TrackFilter

    @detail_route()
    def requestDownload(self, request, pk=None):
        track = self.get_object()
        path = settings.DOWNLOAD_BASE_PATH + 'music/hi/' + format(
            track.release.id,
            '07') + '/' + format(track.release.id, '07') + '-' + format(
                track.tracknum, '02') + '.mp3'
        link = DownloadLink(name=track.tracktitle, path=path)
        link.save()
        finalUrl = request.build_absolute_uri(
            '/download/' + str(link.id) + '/')
        return HttpResponse('{"url":"' + finalUrl + '"}')
