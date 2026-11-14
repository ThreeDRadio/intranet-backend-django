from rest_framework import serializers

from message_bank.models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "code",
            "title",
            "type",
            "created",
            "expirydate",
            "fldproducer",
            "duration",
        )
