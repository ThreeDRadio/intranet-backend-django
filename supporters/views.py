from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.forms.models import modelformset_factory
from django.contrib import messages
import django_filters
from rest_framework import filters
from rest_framework import generics
from rest_framework  import permissions
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.views import APIView
from rest_framework.decorators import  action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import unicodecsv as csv
from datetime import date
from django.db.models import Count
from django.shortcuts import render
from django.conf import settings
from rest_framework import status

from downloads.models import DownloadLink
from session.permissions import IsAuthenticatedOrWhitelist
import os

from .models import Supporter, SupporterNote, Transaction
from .serializers import SupporterSerializer, SupporterNoteSerializer, TransactionSerializer, SupporterTransactionRequest

class DjangoModelPermissionsStrict(permissions.DjangoModelPermissions):
  perms_map = {
      'GET': ['%(app_label)s.view_%(model_name)s'],
      'OPTIONS': [],
      'HEAD': [],
      'POST': ['%(app_label)s.add_%(model_name)s'],
      'PUT': ['%(app_label)s.change_%(model_name)s'],
      'PATCH': ['%(app_label)s.change_%(model_name)s'],
      'DELETE': ['%(app_label)s.delete_%(model_name)s'],
  }

class SupporterViewSet(viewsets.ModelViewSet):
  permission_classes = (DjangoModelPermissionsStrict,)
  queryset = Supporter.objects.filter(excluded = False)
  filter_backends = (filters.OrderingFilter, filters.SearchFilter,
                     django_filters.rest_framework.DjangoFilterBackend)
  serializer_class = SupporterSerializer
  ordering_fields = ('last_name','id','town')
  search_fields = ('last_name','=id')
  pagination_class = LimitOffsetPagination


  @action(detail=True)
  def notes(self, request, pk=None):
    supporter = self.get_object()
    serializer = SupporterNoteSerializer(
        supporter.notes.all().order_by('-created_at'),
        context={'request': request},
        many=True)
    return Response(serializer.data)

  @action(methods=['get','post'], detail=True)
  def transactions(self, request, pk=None):
    if request.method == 'GET':
      supporter = self.get_object()
      serializer = TransactionSerializer(
          supporter.transactions.all().order_by('-created_at'),
          context={'request': request},
          many=True)
      return Response(serializer.data)
    elif request.method == 'POST':
      supporter = self.get_object()
      user = request.user
      transaction_request = SupporterTransactionRequest(data=request.data)
      if transaction_request.is_valid():
        transaction = Transaction(**transaction_request.validated_data)
        transaction.supporter = supporter
        transaction.author = user
        transaction.save()
        response_serializer = TransactionSerializer(transaction)
        return Response(response_serializer.data)
      else:
        return Response(transaction_request.errors, status=status.HTTP_400_BAD_REQUEST)
      return Response()
    



class SupporterNoteViewSet(viewsets.ModelViewSet):
  permission_classes = (permissions.DjangoModelPermissions,)
  queryset = SupporterNote.objects.all()
  serializer_class = SupporterNoteSerializer 
  pagination_class = LimitOffsetPagination


class TransactionFilter(django_filters.FilterSet):

  class Meta:
    model = Transaction
    fields = ('id','created_at','supporter__last_name','expires_at','supporter','author','payment_processed','pack_sent','transaction_type','note','shipping')

class TransactionViewSet(viewsets.ModelViewSet):
  permission_classes = (DjangoModelPermissionsStrict,)
  queryset = Transaction.objects.all()
  serializer_class = TransactionSerializer 
  pagination_class = LimitOffsetPagination
  filter_backends = (filters.OrderingFilter, filters.SearchFilter,
                     django_filters.rest_framework.DjangoFilterBackend)
  filter_class = TransactionFilter
  search_fields = ('supporter__last_name','=supporter__id')
