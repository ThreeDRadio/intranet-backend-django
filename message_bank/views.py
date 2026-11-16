import django_filters
from rest_framework import filters, viewsets

from message_bank.filters import MessagesFilter
from message_bank.models import Message, MessageType
from message_bank.serializers import MessageSerializer, MessageTypeSerializer
from session.permissions import IsAuthenticatedOrWhitelist


class MessagesViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticatedOrWhitelist,
    ]
    queryset = Message.objects.all().order_by("-created")
    ordering_fields = (
        "created",
        "expirydate",
    )
    serializer_class = MessageSerializer
    filterset_class = MessagesFilter
    filter_backends = (
        filters.OrderingFilter,
        django_filters.rest_framework.DjangoFilterBackend,
    )


class MessageTypesViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticatedOrWhitelist,
    ]
    queryset = MessageType.objects.all().order_by("type")
    serializer_class = MessageTypeSerializer
