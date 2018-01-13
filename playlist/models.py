from django.db import models
from datetime import timedelta


# from catalogue.models import Cdtrack
# Create your models here.


class Show(models.Model):
    name = models.CharField(max_length=200)
    defaultHost = models.CharField(max_length=200, blank=True)
    startTime = models.TimeField()
    endTime = models.TimeField()

    def __unicode__(self):
        return self.name


class Playlist(models.Model):
    show = models.ForeignKey(Show, on_delete=models.PROTECT, null=True, related_name="playlists")
    showname = models.CharField(max_length=200, blank=True)
    host = models.CharField(max_length=200)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    complete = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.show) + ' - ' + str(self.date)


class PlaylistEntry(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.PROTECT, related_name='tracks')

    # entry order!
    index = models.IntegerField(null=True)

    # text entry
    artist = models.CharField(max_length=200, blank=False, null=False)
    album = models.CharField(max_length=200, blank=False, null=False)
    title = models.CharField(max_length=200, blank=False, null=False)
    duration = models.DurationField(blank=True, null=True, default=timedelta())

    # quotas
    local = models.BooleanField()
    australian = models.BooleanField()
    female = models.BooleanField()
    newRelease = models.BooleanField()

    # found in catalogue
    #catalogueEntry = models.ForeignKey(Cdtrack, null=True)

    def __unicode__(self):
        return '(' + self.playlist.show + ') ' + self.artist + " - " + self.title
