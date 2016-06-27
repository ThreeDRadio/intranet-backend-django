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

from .forms import NewPlaylistForm, PlaylistEntryForm, SummaryReportForm
from .models import Playlist, PlaylistEntry, Cd, Cdtrack, Show
from serializers import ReleaseSerializer, TrackSerializer, ShowSerializer, PlaylistSerializer, PlaylistEntrySerializer, TopArtistSerializer, ShowStatisticsSerializer, PlayCountSerializer

import logging


# Create your views here.
def summary(request):
    startDate = request.GET.get('startDate', date.min)
    endDate = request.GET.get('endDate', date.max)
    reportFormat = request.GET.get('format')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="play_summary.csv"'

    if reportFormat == "top20":
        playlists = Playlist.objects.filter(date__range=(startDate, endDate))
        out = csv.writer(response)
        out.writerow(['show', 'date', 'start time', 'artist', 'track', 'album',
                      'local', 'australian', 'female', 'new release'])

        for playlist in playlists:
            if playlist.show is None:
                showname = playlist.showname
                startTime = '0:00'
            else:
                showname = playlist.show.name
                startTime = playlist.show.startTime

            for track in playlist.tracks.all():
                out.writerow(
                    [showname, playlist.date, startTime, track.artist, track.title, track.album, track.local, track.australian,
                     track.female, track.newRelease])

    else:
        out = csv.writer(response)
        out.writerow(['Title of Work', 'Composer/Arranger', 'Artist', 'Record Label', 'Total No Usages Per Week', 'Duration',
                      'APRA use only'])

        songs = PlaylistEntry.objects.filter(playlist__date__range=(startDate, endDate)).values('artist', 'title', 'duration').annotate(plays=Count('duration')).order_by('artist','title', '-plays')

        for song in songs:
            out.writerow([song['title'], '', song['artist'], '', song['plays'], song['duration'], ''])

    return response


def playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id)

    tracks = PlaylistEntry.objects.filter(playlist_id=playlist.pk).order_by("pk")

    context = RequestContext(request, {
        'playlist': playlist,
        'tracks': tracks,
    })

    if request.method == 'GET':
        if request.GET.get('format') == 'text':
            if request.GET.get('album') == 'true':
                context.push({'printalbum': True})
            response = render(request, 'playlist/textview.html', context)
            response['Content-Type'] = 'text/plain; charset=utf-8'
            return response

        elif request.GET.get('format') == 'csv':
            response = HttpResponse(content_type='text/csv')
            if playlist.show is None:
                response[
                    'Content-Disposition'] = 'attachment; filename="' + playlist.showname + '-' + playlist.date.isoformat() + '.csv"'
            else:
                response[
                    'Content-Disposition'] = 'attachment; filename="' + playlist.show.name + '-' + playlist.date.isoformat() + '.csv"'

            out = csv.writer(response)
            out.writerow(['artist', 'track', 'album', 'local', 'australian', 'female', 'new release'])

            for track in playlist.tracks.all():
                out.writerow([track.artist, track.title, track.album, track.local, track.australian, track.female,
                              track.newRelease])
            return response


def reports(request):
    if request.method == 'POST':
        form = SummaryReportForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/logger/summary/?startDate=' + unicode(form.cleaned_data.get('startDate')) +
                                        '&endDate=' + unicode(form.cleaned_data.get('endDate')) + '&format=' + unicode(form.cleaned_data.get('reportFormat')))
    else:
        form = SummaryReportForm()
    context = RequestContext(request, {
        'form': form,
    })
    return render(request, 'playlist/reports.html', context)

###############


class ReleaseViewSet(viewsets.ModelViewSet):
    queryset = Cd.objects.all()
    serializer_class = ReleaseSerializer
    filter_backends = (filters.OrderingFilter,
                       filters.SearchFilter,)
    search_fields = ('artist', 'title', 'tracks__title')
    ordering_fields = ('arrivaldate', 'artist', 'title')

    @list_route()
    def latest(self, request):
        latestReleases = Cd.objects.all().order_by('-arrivaldate')

        page = self.paginate_queryset(latestReleases)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(latestReleases, many=True)
        return Response(serializer.data)


class TrackFilter(django_filters.FilterSet):
    artist = django_filters.CharFilter(name="album__artist", lookup_type='icontains')
    track = django_filters.CharFilter(name="tracktitle", lookup_type='icontains')

    class Meta:
        model = Cdtrack
        fields = ['track', 'artist']


class TrackViewSet(viewsets.ModelViewSet):
    queryset = Cdtrack.objects.all()
    serializer_class = TrackSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = TrackFilter

class ShowViewSet(viewsets.ModelViewSet):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer
    pagination_class = None

    @detail_route()
    def topartists(self, request, pk=None):
        show = self.get_object()
        top = PlaylistEntry.objects.filter(playlist__show=show).values('artist').annotate(plays=Count('artist')).order_by('-plays')[:10]
        serializer = TopArtistSerializer(top, many=True)
        return Response(serializer.data)

    @detail_route()
    def statistics(self, request, pk=None):
        show = self.get_object()
        tracks = PlaylistEntry.objects.filter(playlist__show=show).count()
        local = PlaylistEntry.objects.filter(playlist__show=show).filter(local=True).count()
        australian = PlaylistEntry.objects.filter(playlist__show=show).filter(australian=True).count()
        female = PlaylistEntry.objects.filter(playlist__show=show).filter(female=True).count()
        artists = PlaylistEntry.objects.filter(playlist__show=show).distinct('artist').count()

        data = (
                {
                    'name': 'Total tracks',
                    'value': tracks
                },
                {   'name': 'Unique artists',
                    'value': artists
                },
                {
                    'name': 'Local',
                    'value': local
                }, 
                {
                    'name': 'Australian',
                    'value': australian
                },
                {
                    'name': 'Female',
                    'value': female
                },
            )

        serializer = ShowStatisticsSerializer(data, context={'request': request}, many=True)

        return Response(serializer.data)

    @detail_route()
    def playlists (self, request, pk=None):
        show = self.get_object()
        serializer = PlaylistSerializer(show.playlists.all().order_by('-date'), context={'request': request}, many=True)
        return Response(serializer.data)

class PlaylistViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.OrderingFilter,)
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    ordering_fields = ('date',)

    @detail_route()
    def tracks(self, request, pk=None):
        post = self.get_object()
        serializer = PlaylistEntrySerializer(post.tracks.all().order_by('index','pk'), context={'request': request}, many=True)
        return Response(serializer.data)

class PlaylistEntryViewSet(viewsets.ModelViewSet):
    queryset = PlaylistEntry.objects.all()
    serializer_class = PlaylistEntrySerializer

    @list_route()
    def today(self, request):
        queryset = PlaylistEntry.objects.filter(playlist__date=date.today()).values('artist', 'title', 'album').annotate(plays=Count('title')).order_by('artist', '-plays')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PlayCountSerializer(page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PlayCountSerializer(queryset, many=True)
        return Response(serializer.data)


class ArtistViewSet(viewsets.ViewSet):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('artist',)

    def list(self, request):
        searchParam = self.request.query_params.get('term')
        if searchParam is None:
            artists = [release.artist for release in Cd.objects.distinct('artist').order_by('artist')]
        else:
            artists = [release.artist for release in
                       Cd.objects.distinct('artist').filter(artist__icontains=searchParam).order_by('artist')]

        return Response(artists)

