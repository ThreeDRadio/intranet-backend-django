from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.forms.models import modelformset_factory
from django.contrib import messages
import django_filters
from rest_framework import filters
from rest_framework import generics
from rest_framework  import permissions
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import unicodecsv as csv
from datetime import date
from django.db.models import Count
from django.shortcuts import render
from django.conf import settings

from .models import Comment, Release, Track
from .serializers import CommentSerializer, ReleaseSerializer, TrackSerializer, CommentSerializer
from downloads.models import DownloadLink
from session.permissions import IsAuthenticatedOrWhitelist
import os

# Create your views here.
class ArtistViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)
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
  min_arrival = django_filters.DateFilter(field_name="arrivaldate", lookup_expr="gte")
  artist = django_filters.CharFilter(field_name="artist", lookup_expr="icontains")
  track  = django_filters.CharFilter(field_name="tracks__tracktitle", lookup_expr="icontains")
  country = django_filters.CharFilter(field_name="cpa", lookup_expr="icontains")
  release = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
  

  class Meta:
    model = Release
    fields = [
      'arrivaldate', 'artist', 'tracks__tracktitle', 'year', 'country',
      'title', 'local', 'demo', 'compilation', 'female'
    ]


class ReleaseViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer
    filter_backends = (filters.OrderingFilter, filters.SearchFilter,
                       django_filters.rest_framework.DjangoFilterBackend)
    search_fields = ('artist', 'title', 'tracks__tracktitle')
    ordering_fields = ('arrivaldate', 'artist', 'title','year','createwhen')
    filter_class = ReleaseFilter
    pagination_class = LimitOffsetPagination

    @action(detail=True)
    def tracks(self, request, pk=None):
        release = self.get_object()
        serializer = TrackSerializer(
            release.tracks.all().order_by('tracknum'),
            context={'request': request},
            many=True)
        return Response(serializer.data)

    @action(detail=True)
    def comments(self, request, pk=None):
        release = self.get_object()
        serializer = CommentSerializer(
            release.comments.all().order_by('pk'),
            context={'request': request},
            many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Comment.objects.filter(visible = True)
    serializer_class = CommentSerializer
    filter_backends = (filters.OrderingFilter, filters.SearchFilter,
                       django_filters.rest_framework.DjangoFilterBackend)
    ordering_fields = ('createwhen',)
    pagination_class = LimitOffsetPagination

class TrackFilter(django_filters.FilterSet):
    artist = django_filters.CharFilter(field_name="album__artist", lookup_expr='icontains')
    track = django_filters.CharFilter(field_name="tracktitle", lookup_expr='icontains')
    needsencoding = django_filters.BooleanFilter(field_name="needsencoding")

    class Meta:
        model = Track
        fields = ['track', 'artist','needsencoding']


class TrackViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    filter_class = TrackFilter


    @action(methods=['post'],detail=True)
    def audio(self, request, pk=None):
        track = self.get_object()
        file = request.FILES['file']
        directory = os.path.dirname(track.hiPath)
        if not os.path.exists(directory):
            os.makedirs(directory, 0o777)
        with open(track.hiPath, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        serializer = TrackSerializer(track)
        return Response(serializer.data)


    @action(detail=True, url_path='download/(?P<quality>[a-z]+)')
    def download(self, request, quality, pk=None ):
        f = 'hi'
        if quality== 'lo':
            f = 'lo'
        elif quality == 'hi':
            f = 'hi'
        else:
            raise Http404

        track = get_object_or_404(Track, pk=pk)
        path = settings.DOWNLOAD_BASE_PATH + 'music/'+ f + '/' + format(
            track.release.id,
            '07') + '/' + format(track.release.id, '07') + '-' + format(
                track.tracknum, '02') + '.mp3'
        link = DownloadLink(name=track.tracktitle, path=path)
        link.save()
        finalUrl = request.build_absolute_uri(
            settings.API_PREFIX + 'download/' + str(link.id) + '/')
        return HttpResponse('{"url":"' + finalUrl + '"}')
