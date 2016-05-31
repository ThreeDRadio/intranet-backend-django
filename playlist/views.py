from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.forms.models import modelformset_factory
from django.contrib import messages
import django_filters
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import unicodecsv as csv
from datetime import date
from django.db.models import Count

from .forms import NewPlaylistForm, PlaylistEntryForm, SummaryReportForm
from .models import Playlist, PlaylistEntry, Cd, Cdtrack, Show
from serializers import ReleaseSerializer, TrackSerializer, ShowSerializer, PlaylistSerializer, PlaylistEntrySerializer


# Create your views here.

def index(request):
    songCount = PlaylistEntry.objects.all().count()
    local = PlaylistEntry.objects.filter(local=True).count()
    australian = PlaylistEntry.objects.filter(australian=True).count()
    female = PlaylistEntry.objects.filter(female=True).count()
    artists = PlaylistEntry.objects.distinct('artist').count()
    top = PlaylistEntry.objects.values('artist').annotate(plays=Count('artist')).order_by('-plays')[:10]

    playlists = Playlist.objects.order_by('date').order_by('-pk')
    if request.GET.get('saved') == 'true':
        messages.success(request, 'Playlist Submitted.')
    context = RequestContext(request, {
        'playlists': playlists,
        'songCount': songCount,
        'artists': artists,
        'local': local,
        'australian': australian,
        'female': female,
        'top': top,
    })
    return render(request, 'playlist/index.html', context)


def today(request):
    songs = PlaylistEntry.objects.filter(playlist__date=date.today()).values('artist', 'title', 'album').annotate(plays=Count('title')).order_by('-plays')
    context = RequestContext(request, {
        'songs': songs,
    })
    return render(request, 'playlist/today.html', context)


def summary(request):
    startDate = request.GET.get('startDate', date.min)
    endDate = request.GET.get('endDate', date.max)
    playlists = Playlist.objects.filter(date__range=(startDate, endDate))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="play_summary.csv"'

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

        for track in playlist.playlistentry_set.all():
            out.writerow(
                [showname, playlist.date, startTime, track.artist, track.title, track.album, track.local, track.australian,
                 track.female, track.newRelease])

    return response


def new(request):
    if request.method == 'POST':
        form = NewPlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save()
            return HttpResponseRedirect('/logger/playlists/' + str(playlist.id) + '/edit/')
        else:
            context = RequestContext(request, {
                'form': form,
                'shows': Show.objects.all()
            })
            return render(request, 'playlist/new.html', context)

    else:
        form = NewPlaylistForm()
        context = RequestContext(request, {
            'form': form,
            'shows': Show.objects.all()
        })
        return render(request, 'playlist/new.html', context)


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

            for track in playlist.playlistentry_set.all():
                out.writerow([track.artist, track.title, track.album, track.local, track.australian, track.female,
                              track.newRelease])
            return response
    return render(request, "playlist/view.html", context)


def edit(request, playlist_id):
    playlist = Playlist.objects.get(pk=playlist_id)

    EntryFormSet = modelformset_factory(PlaylistEntry, extra=60, form=PlaylistEntryForm)
    formset = EntryFormSet(queryset=PlaylistEntry.objects.filter(playlist=playlist))

    if request.method == 'POST':
        formset = EntryFormSet(request.POST)
        if formset.is_valid():
            playlistEntries = formset.save(commit=False)
            for entry in playlistEntries:
                entry.playlist = playlist
                entry.save()

            if request.POST.get('final'):
                playlist.complete = True
                playlist.save()
                return HttpResponseRedirect('/logger/?saved=true')
        else:
            messages.error(request,
                           'You have invalid data in your logging sheet. Please fix the problems and try saving again..')
            context = RequestContext(request, {
                'playlist': playlist,
                'formset': formset,
            })

            return render(request, 'playlist/edit.html', context)

        formset = EntryFormSet(queryset=PlaylistEntry.objects.filter(playlist=playlist))
        messages.success(request, 'Playlist saved.')

    context = RequestContext(request, {
        'playlist': playlist,
        'formset': formset,
    })

    return render(request, 'playlist/edit.html', context)


def shows(request, show_id):
    show = get_object_or_404(Show, pk=show_id)
    playlists = show.playlists.order_by('-date')
    songCount = PlaylistEntry.objects.filter(playlist__show=show).count()
    local = PlaylistEntry.objects.filter(playlist__show=show).filter(local=True).count()
    australian = PlaylistEntry.objects.filter(playlist__show=show).filter(australian=True).count()
    female = PlaylistEntry.objects.filter(playlist__show=show).filter(female=True).count()
    artists = PlaylistEntry.objects.filter(playlist__show=show).distinct('artist').count()
    top = PlaylistEntry.objects.filter(playlist__show=show).values('artist').annotate(plays=Count('artist')).order_by('-plays')[:10]
    context = RequestContext(request, {
        'show': show,
        'playlists': playlists,
        'songCount': songCount,
        'artists': artists,
        'local': local,
        'australian': australian,
        'female': female,
        'top': top,
    })

    return render(request, 'playlist/show.html', context)


def reports(request):
    if request.method == 'POST':
        form = SummaryReportForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/logger/summary/?startDate=' + unicode(form.cleaned_data.get('startDate')) +
                                        '&endDate=' + unicode(form.cleaned_data.get('endDate')))
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

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

class PlaylistEntryViewSet(viewsets.ModelViewSet):
    queryset = PlaylistEntry.objects.all()
    serializer_class = PlaylistEntrySerializer

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
