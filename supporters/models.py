from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

class Supporter(models.Model):
  first_name = models.CharField(max_length = 200)
  last_name = models.CharField(max_length = 200)
  address1 = models.CharField(max_length = 200)
  address2 = models.CharField(max_length = 200, blank=True)
  town = models.CharField(max_length = 200)
  state = models.CharField(max_length = 200)
  postcode = models.CharField(max_length = 200)
  country = models.CharField(max_length = 200, blank=True)

  phone_mobile = models.CharField(max_length = 200, blank=True)
  phone_home = models.CharField(max_length = 200, blank=True)
  phone_work = models.CharField(max_length = 200, blank=True)
  email = models.CharField(max_length = 200, blank=True)
  gender = models.CharField(max_length = 200, blank=True)
  dob = models.DateField()
  excluded = models.BooleanField(default=False, blank=True)
  prefer_email = models.BooleanField(default=True, blank=True)

  def __str__(self):
    return str(self.first_name) + str(self.last_name)

  def __unicode__(self):
    return str(self.first_name) + str(self.last_name)


class SupporterNote(models.Model):
  supporter = models.ForeignKey(Supporter, on_delete=models.PROTECT, related_name='notes')
  author = models.ForeignKey(User, on_delete=models.PROTECT)
  created_at = models.DateTimeField(auto_now_add=True)
  note = models.TextField()