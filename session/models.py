from django.db import models
from django.contrib.auth.models import User 
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender = User)
def init_new_user(sender, instance, signal, created, **kqargs):
    if created:
        Token.objects.create(user = instance)


class OldPassword(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    password = models.CharField(max_length=200)

class Whitelist(models.Model):
    ip = models.GenericIPAddressField()
    name = models.CharField(max_length=200)

class OldUser(models.Model):
    """ A model that matches the original users table, for importing"""
    id = models.BigIntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100, blank=True, null=True)
    first = models.CharField(max_length=100, blank=True, null=True)
    last = models.CharField(max_length=100, blank=True, null=True)
    admin = models.NullBooleanField()
    active = models.NullBooleanField()
    cdeditor = models.NullBooleanField()
    adminbook = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'users'
