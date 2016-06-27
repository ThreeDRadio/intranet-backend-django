from django.shortcuts import render
from django.conf import settings 
from rest_framework import status
from django.contrib.auth import authenticate, logout, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth.models import User

from serializers import UserSerializer
from permissions import IsStaffOrTargetUser

class UserViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        return (IsStaffOrTargetUser() ,)

    def retrieve(self, request, pk=None):
        if pk == 'me':
            return Response(UserSerializer(request.user).data)
        return super(UserViewSet, self).retrieve(request, pk)


