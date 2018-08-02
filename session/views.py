from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from django.contrib.auth import authenticate, logout, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest

from .serializers import UserSerializer
from .permissions import IsStaffOrTargetUser
from hashlib import md5

from .models import OldPassword


class UserViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [
        IsStaffOrTargetUser,
    ]

    def retrieve(self, request, pk=None):
        if pk == 'me':
            if request.user.is_authenticated:
                self.check_object_permissions(request, request.user)
                return Response(UserSerializer(request.user).data)
            else:
                return HttpResponseBadRequest()

        return super(UserViewSet, self).retrieve(request, pk)


class MigrateAndLogin(APIView):
    error_messages = {
        'invalid': "Invalid username or password",
        'disabled': "Sorry, this account is suspended",
    }

    def _error_response(self, messageKey):
        data = {
            'success': False,
            'message': self.error_messages[messageKey],
            'user_id': None,
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def getOldPassword(self, username):
        if OldPassword.objects.filter(user__username=username).exists():
            return OldPassword.objects.get(user__username=username)
        return None

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        errors = {}
        error = False
        if username is None:
            error = True
            errors['username'] = "This field is required"

        if password is None:
            error = True
            errors['password'] = "This field is required"

        # Return errors if the username/password was empty
        if error == True:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Try authenticating with the posted data
        user = authenticate(username=username, password=password)
        if user is not None:
            return Response({'token': user.auth_token.key, 'userId': user.id})

        # Try to migrate their password
        oldPassword = self.getOldPassword(username)
        if oldPassword is not None:
            passwordHash = md5(password.encode('utf-8')).hexdigest()
            if oldPassword.password == passwordHash:
                user = oldPassword.user
                user.set_password(password)
                user.save()
                oldPassword.delete()
                return Response({
                    'token': user.auth_token.key,
                    'user': user.id
                })

        return self._error_response('invalid')
