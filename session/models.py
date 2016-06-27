from django.db import models
from django.contrib.auth.models import User 
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender = User)
def init_new_user(sender, instance, signal, created, **kqargs):
    if created:
        Token.objects.create(user = instance)



class Whitelist(models.Model):
    ip = models.GenericIPAddressField()
    name = models.CharField(max_length=200)
