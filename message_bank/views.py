from rest_framework import viewsets

from message_bank.models import Message, MessageType
from message_bank.serializers import MessageSerializer, MessageTypeSerializer
from session.permissions import IsAuthenticatedOrWhitelist


class MessagesViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticatedOrWhitelist,
    ]
    queryset = Message.objects.all().order_by("-created")
    ordering_fields = ("created",)
    serializer_class = MessageSerializer


class MessageTypesViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticatedOrWhitelist,
    ]
    queryset = MessageType.objects.all().order_by("type")
    serializer_class = MessageTypeSerializer
