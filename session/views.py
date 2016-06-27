from django.shortcuts import render
from django.conf import settings 
from rest_framework import status
from django.contrib.auth import authenticate, logout, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest

from serializers import UserSerializer
from permissions import IsStaffOrTargetUser

class UserViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsStaffOrTargetUser,]


    def retrieve(self, request, pk=None):
        if pk == 'me':
            if request.user.is_authenticated():
                self.check_object_permissions(request, request.user)
                return Response(UserSerializer(request.user).data)
            else:
                return HttpResponseBadRequest()

        return super(UserViewSet, self).retrieve(request, pk)


