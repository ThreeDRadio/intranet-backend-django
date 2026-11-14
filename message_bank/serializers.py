from rest_framework import serializers

from message_bank.models import Message, MessageType


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "code",
            "title",
            "type",
            "created",
            "nq",
            "expirydate",
            "fldproducer",
            "duration",
        )


class MessageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageType
        fields = ("type", "description", "scheduled")
