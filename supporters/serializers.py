from rest_framework import serializers
from .models import Supporter, SupporterNote, Transaction
from django.contrib.auth.models import User 
import urllib, hashlib



class SupporterSerializer(serializers.ModelSerializer):

  class Meta:
    model = Supporter
    fields = ('id','first_name','last_name','address1','address2','town','state','postcode','country','phone_mobile','phone_home','phone_work','email','gender','dob','excluded','prefer_email')

class SupporterNoteSerializer(serializers.ModelSerializer):

  class Meta:
    model = SupporterNote
    fields = ('supporter','author','created_at','note')


class TransactionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Transaction
    fields = ('id','created_at','expires_at','supporter','author','payment_processed','pack_sent','transaction_type','note')

class SupporterTransactionRequest(serializers.ModelSerializer):
  class Meta:
    model = Transaction
    fields = ('expires_at','payment_processed','transaction_type','note')
