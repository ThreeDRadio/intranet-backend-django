from django.db import models
from django.conf import settings
import os.path

# Create your models here.
class Release(models.Model):
    id = models.BigAutoField(primary_key=True)
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


class Comment(models.Model):
    release = models.ForeignKey(Release, on_delete=models.PROTECT, db_column='cdid', related_name="comments")
    
    cdtrackid = models.BigIntegerField()
    comment = models.TextField(blank=True, null=True)
    createwho = models.BigIntegerField()
    createwhen = models.BigIntegerField()
    modifywho = models.BigIntegerField()
    modifywhen = models.BigIntegerField()

    class Meta:
        db_table = 'cdcomment'

    def __unicode__(self):
        return self.comment 

class Track(models.Model):
    id = models.BigAutoField(db_column='trackid', primary_key=True)
    release = models.ForeignKey(Release, on_delete=models.PROTECT, db_column='cdid', related_name="tracks")
    tracknum = models.BigIntegerField()
    tracktitle = models.CharField(max_length=200, blank=True, null=True)
    trackartist = models.CharField(max_length=200, blank=True, null=True)
    tracklength = models.BigIntegerField(blank=True, null=True)

    @property
    def hiPath(self): 
        return settings.DOWNLOAD_BASE_PATH + 'music/hi/' + format(
            self.release.id,
            '07') + '/' + format(self.release.id, '07') + '-' + format(
                self.tracknum, '02') + '.mp3'

    def loPath(self): 
        return settings.DOWNLOAD_BASE_PATH + 'music/lo/' + format(
            self.release.id,
            '07') + '/' + format(self.release.id, '07') + '-' + format(
                self.tracknum, '02') + '.mp3'
    
    @property
    def hiAvailable(self):
        return os.path.exists(self.hiPath)

    class Meta:
        db_table = 'cdtrack'
