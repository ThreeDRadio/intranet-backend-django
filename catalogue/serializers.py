from rest_framework import serializers
from .models import Release, Track

class TrackSerializer(serializers.ModelSerializer):
    cdid = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Track
        fields = ('trackid', 'url', 'tracknum', 'trackartist', 'tracktitle', 'tracklength', 'cdid')

class ReleaseSerializer(serializers.HyperlinkedModelSerializer):
    tracks = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Release 
        fields = ('id', 'url', 'arrivaldate', 'artist', 'title', 'year', 'local', 'compilation', 'female', 'tracks')
