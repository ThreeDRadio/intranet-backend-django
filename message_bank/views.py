from rest_framework import viewsets

from message_bank.models import Message
from message_bank.serializers import MessageSerializer
from session.permissions import IsAuthenticatedOrWhitelist


class MessagesViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticatedOrWhitelist,
    ]
    queryset = Message.objects.all().order_by("-created")
    ordering_fields = ("created",)
    serializer_class = MessageSerializer
