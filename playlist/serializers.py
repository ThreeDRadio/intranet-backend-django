from rest_framework import serializers
from .models import Cd, Cdtrack, Show, Playlist, PlaylistEntry


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

class ShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Show
        fields = ('id', 'name', 'startTime', 'endTime', 'defaultHost') 

class PlaylistEntrySerializer(serializers.ModelSerializer):
    playlist = serializers.PrimaryKeyRelatedField(
            queryset = Playlist.objects.all()
    )

    class Meta:
        model = PlaylistEntry
        fields = ('id', 'artist','album','title','duration','local','australian','female','newRelease','playlist' )
    pass

class PlaylistSerializer(serializers.ModelSerializer):
    entries =PlaylistEntrySerializer( 
            many=True,
            read_only=True
    )

    class Meta:
        model = Playlist
        fields = ('id', 'show','showname', 'host', 'date', 'notes', 'entries')
