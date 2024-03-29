from django.db import models
from datetime import timedelta
from django.db.models.signals import post_save, pre_save


# from catalogue.models import Cdtrack
# Create your models here.


class Show(models.Model):
    name = models.CharField(max_length=200)
    defaultHost = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    startTime = models.TimeField()
    endTime = models.TimeField()

    customQuotas = models.BooleanField(default=False)
    femaleQuota = models.IntegerField(null=True, blank=True)
    localQuota = models.IntegerField(null=True, blank=True)
    australianQuota = models.IntegerField(null=True, blank=True)

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

    # Whether this has been sent to the website
    published= models.BooleanField(default=False)
    fillin = models.BooleanField(default=False)

    # We record the quotas required for each playlist, to account for changes over time
    femaleQuota = models.IntegerField(blank=True)
    localQuota = models.IntegerField(blank=True)
    australianQuota = models.IntegerField(blank=True)

    @classmethod
    def applyQuotas(cls, sender, instance, raw, using, update_fields, *args, **kwargs):
        print('Applying Quotas')
        if instance.pk == None:
            if instance.show.customQuotas:
                instance.femaleQuota = instance.show.femaleQuota
                instance.localQuota= instance.show.localQuota
                instance.australianQuota= instance.show.australianQuota
            else:
                instance.femaleQuota = int(Setting.objects.get(pk="female_quota").value)
                instance.localQuota = int(Setting.objects.get(pk="local_quota").value)
                instance.australianQuota = int(Setting.objects.get(pk="australian_quota").value)

    def __unicode__(self):
        return str(self.show) + ' - ' + str(self.date)

    def __str__(self):
        return str(self.show) + ' - ' + str(self.date)

pre_save.connect(Playlist.applyQuotas, sender=Playlist)

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
