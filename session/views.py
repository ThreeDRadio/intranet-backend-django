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

class SessionView(APIView):
    error_messages = {
            'invalid': "Invalid username or password",
            'disabled': "Sorry, this account is suspended",
            }

    def _error_response(self, messageKey):
        data = {
                'success' : False,
                'message' : self.error_messages[messageKey],
                'user_id' : None,
                }
        return Response(data)

    def get(self, request):
        if request.user.is_authenticated():
            return Response({'user_id': request.user.id})

        elif settings.INTRANET_AUTH['ip'] == request.META['REMOTE_ADDR']:
                user = authenticate(username=settings.INTRANET_AUTH['username'], password=settings.INTRANET_AUTH['password'])
                login(request, user)
                return Response({'user_id': user.id})

        return Response({'user_id': None})

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return Response({'success': True, 'user_id': user.id})
                
            return self._error_response('disabled')
        return self._error_response('invalid')

    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


