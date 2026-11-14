# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Message(models.Model):
    code = models.CharField(primary_key=True, max_length=6)
    title = models.CharField(max_length=30)
    type = models.CharField(max_length=20)
    nq = models.CharField(max_length=30)
    expirydate = models.DateField()
    filename = models.CharField(max_length=32)
    fldproducer = models.CharField(max_length=50, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'messagelist'


class Playlog(models.Model):
    when_played = models.DateTimeField()
    id_code = models.CharField(max_length=15)
    id_type = models.CharField(max_length=3)
    hostname = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'playlog'


class Programmes(models.Model):
    code = models.CharField(primary_key=True, max_length=6)
    name = models.CharField(max_length=36)
    day = models.CharField(max_length=9)
    start = models.TimeField(blank=True, null=True)
    presenters = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=70, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'programmes'


class Schedule(models.Model):
    msg_code = models.CharField(max_length=6)
    time_date = models.DateTimeField()
    msg_order = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'schedule'


class Tbladmin(models.Model):
    fldadmin = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'tbladmin'


class MessageType(models.Model):
    type = models.CharField(primary_key=True, max_length=20)
    description = models.CharField(max_length=70)
    scheduled = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'typelist'
