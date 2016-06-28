from rest_framework import serializers
from .models import Cd, Cdtrack

class TrackSerializer(serializers.ModelSerializer):
    album = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Cdtrack
        fields = ('trackid', 'url', 'tracknum', 'trackartist', 'tracktitle', 'tracklength', 'album')

class ReleaseSerializer(serializers.HyperlinkedModelSerializer):
    tracks = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Cd
        fields = ('id', 'url', 'arrivaldate', 'artist', 'title', 'year', 'local', 'compilation', 'female', 'tracks')
