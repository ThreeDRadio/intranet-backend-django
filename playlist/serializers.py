from rest_framework import serializers

from .models import Show, Playlist, PlaylistEntry



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


class ShowSerializer(serializers.ModelSerializer):
    playlists = serializers.HyperlinkedIdentityField(view_name='Show-playlists')
    topartists = serializers.HyperlinkedIdentityField(view_name='Show-topartists')
    statistics = serializers.HyperlinkedIdentityField(view_name='Show-statistics')

    class Meta:
        model = Show
        fields = ('id', 'name', 'startTime', 'endTime', 'defaultHost', 'playlists', 'topartists', 'statistics','customQuotas','femaleQuota','localQuota','australianQuota') 

class PlaylistEntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = PlaylistEntry
        fields = ('id','index', 'artist','album','title','duration','local','australian','female','newRelease','playlist' )
    pass

class PlaylistSerializer(serializers.ModelSerializer):

    tracks = serializers.HyperlinkedIdentityField(view_name='Playlist-tracks')

    class Meta:
        model = Playlist
        fields = ('id', 'show','showname', 'host', 'date', 'notes', 'tracks', 'complete','femaleQuota','localQuota','australianQuota')
