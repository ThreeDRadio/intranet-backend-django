from django.db import models
from datetime import timedelta


# Create your models here.


class Cd(models.Model):
    id = models.BigIntegerField(primary_key=True)
    artist = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    year = models.SmallIntegerField(blank=True, null=True)
    genre = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    cpa = models.CharField(max_length=100, blank=True, null=True)
    arrivaldate = models.DateField(blank=True, null=True)
    copies = models.SmallIntegerField(blank=True, null=True)
    compilation = models.SmallIntegerField(blank=True, null=True)
    demo = models.SmallIntegerField(blank=True, null=True)
    local = models.SmallIntegerField(blank=True, null=True)
    female = models.SmallIntegerField(blank=True, null=True)
    createwho = models.BigIntegerField(blank=True, null=True)
    createwhen = models.BigIntegerField(blank=True, null=True)
    modifywho = models.BigIntegerField(blank=True, null=True)
    modifywhen = models.BigIntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    format = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'cd'

    def __unicode__(self):
        return self.artist + " - " + self.title


class Cdcomment(models.Model):
    cdid = models.BigIntegerField()
    cdtrackid = models.BigIntegerField()
    comment = models.TextField(blank=True, null=True)
    createwho = models.BigIntegerField()
    createwhen = models.BigIntegerField()
    modifywho = models.BigIntegerField()
    modifywhen = models.BigIntegerField()

    class Meta:
        db_table = 'cdcomment'


class Cdtrack(models.Model):
    trackid = models.BigIntegerField(primary_key=True)
    cdid = models.ForeignKey(Cd, db_column='cdid', related_name="tracks")
    tracknum = models.BigIntegerField()
    tracktitle = models.CharField(max_length=200, blank=True, null=True)
    trackartist = models.CharField(max_length=200, blank=True, null=True)
    tracklength = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'cdtrack'


class Show(models.Model):
    name = models.CharField(max_length=200)
    defaultHost = models.CharField(max_length=200, blank=True)
    startTime = models.TimeField()
    endTime = models.TimeField()

    def __unicode__(self):
        return self.name


class Playlist(models.Model):
    show = models.ForeignKey(Show, null=True, related_name="playlists")
    showname = models.CharField(max_length=200, blank=True)
    host = models.CharField(max_length=200)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    complete = models.BooleanField(default=False)

    def __unicode__(self):
        return self.show + ' - ' + str(self.date)


class PlaylistEntry(models.Model):
    playlist = models.ForeignKey(Playlist, related_name='tracks')
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
    catalogueEntry = models.ForeignKey(Cdtrack, null=True)

    def __unicode__(self):
        return '(' + self.playlist.show + ') ' + self.artist + " - " + self.title
