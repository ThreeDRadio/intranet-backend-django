from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

class Supporter(models.Model):
  first_name = models.CharField(max_length = 200, null=True, blank=True)
  last_name = models.CharField(max_length = 200, null=True, blank=True)
  address1 = models.CharField(max_length = 200, null=True, blank=True)
  address2 = models.CharField(max_length = 200, null=True, blank=True)
  town = models.CharField(max_length = 200, null=True, blank=True)
  state = models.CharField(max_length = 200, default='SA', null=True)
  postcode = models.CharField(max_length = 200, null=True, blank=True)
  country = models.CharField(max_length = 200, default='Australia', null=True, blank=True)

  phone_mobile = models.CharField(max_length = 200, null=True, blank=True)
  phone_home = models.CharField(max_length = 200, null=True, blank=True)
  phone_work = models.CharField(max_length = 200, null=True, blank=True)
  email = models.CharField(max_length = 200, null=True, blank=True)
  gender = models.CharField(max_length = 200, null=True, blank=True)
  dob = models.DateField( null=True, blank=True)
  excluded = models.BooleanField(default=False, blank=True)
  prefer_email = models.BooleanField(default=True, blank=True)

  def __str__(self):
    return str(self.first_name) + str(self.last_name)

  def __unicode__(self):
    return str(self.first_name) + str(self.last_name)


class SupporterNote(models.Model):
  supporter = models.ForeignKey(Supporter, on_delete=models.PROTECT, related_name='notes')
  author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='supporter_notes')
  created_at = models.DateTimeField(auto_now_add=True)
  note = models.TextField()

class Transaction(models.Model):
  created_at = models.DateTimeField(auto_now_add=True)
  expires_at = models.DateField()
  supporter = models.ForeignKey(Supporter, on_delete=models.PROTECT, related_name='transactions')
  author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='supporter_transactions')
  payment_processed = models.BooleanField(default=False, blank=True)
  pack_sent = models.BooleanField(default=False, blank=True)
  transaction_type = models.CharField(max_length = 200, null=True)
  note = models.TextField(null=True, blank=True)