from rest_framework import serializers
from .models import Cd, Cdtrack, Show, Playlist, PlaylistEntry


class TrackSerializer(serializers.ModelSerializer):
    album = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Cdtrack
        fields = ('trackid', 'url', 'tracknum', 'trackartist', 'tracktitle', 'tracklength', 'album')


class TopArtistSerializer(serializers.Serializer):
    artist = serializers.CharField()
    plays = serializers.IntegerField()

class ShowStatisticsSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.IntegerField()


class PlayCountSerializer(serializers.Serializer):
    artist = serializers.CharField()
    album = serializers.CharField()
    title = serializers.CharField()
    plays = serializers.IntegerField(
        read_only=True
    )



class ReleaseSerializer(serializers.HyperlinkedModelSerializer):
    tracks = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Cd
        fields = ('id', 'url', 'arrivaldate', 'artist', 'title', 'year', 'local', 'compilation', 'female', 'tracks')

class ShowSerializer(serializers.ModelSerializer):
    playlists = serializers.HyperlinkedIdentityField(view_name='Show-playlists')
    topartists = serializers.HyperlinkedIdentityField(view_name='Show-topartists')
    statistics = serializers.HyperlinkedIdentityField(view_name='Show-statistics')

    class Meta:
        model = Show
        fields = ('id', 'name', 'startTime', 'endTime', 'defaultHost', 'playlists', 'topartists', 'statistics') 

class PlaylistEntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = PlaylistEntry
        fields = ('id','index', 'artist','album','title','duration','local','australian','female','newRelease','playlist' )
    pass

class PlaylistSerializer(serializers.ModelSerializer):

    tracks = serializers.HyperlinkedIdentityField(view_name='Playlist-tracks')

    class Meta:
        model = Playlist
        fields = ('id', 'show','showname', 'host', 'date', 'notes', 'tracks', 'complete')
