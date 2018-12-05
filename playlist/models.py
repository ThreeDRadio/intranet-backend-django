from django.db import models
from datetime import timedelta


# from catalogue.models import Cdtrack
# Create your models here.


class Show(models.Model):
    name = models.CharField(max_length=200)
    defaultHost = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    startTime = models.TimeField()
    endTime = models.TimeField()

    customQuotas = models.BooleanField(default=False)
    femaleQuota = models.IntegerField(null=True)
    localQuota = models.IntegerField(null=True)
    australianQuota = models.IntegerField(null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

class Playlist(models.Model):
    show = models.ForeignKey(Show, on_delete=models.PROTECT, null=True, related_name="playlists")
    showname = models.CharField(max_length=200, blank=True)
    host = models.CharField(max_length=200)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    complete = models.BooleanField(default=False)
    fillin = models.BooleanField(default=False)

    # We record the quotas required for each playlist, to account for changes over time
    femaleQuota = models.IntegerField()
    localQuota = models.IntegerField()
    australianQuota = models.IntegerField()

    def __unicode__(self):
        return str(self.show) + ' - ' + str(self.date)

    def __str__(self):
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

    def __str__(self):
        return '(' + str(self.playlist.show) + ') ' + self.artist + " - " + self.title



class Setting(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    value = models.CharField(max_length=200)
    description = models.TextField()
