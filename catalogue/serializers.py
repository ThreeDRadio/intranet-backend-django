from rest_framework import serializers
from .models import Release, Track, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'comment')

class TrackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Track
        fields = ('id', 'tracknum', 'trackartist', 'tracktitle', 'tracklength', 'release', 'hiAvailable')

class ReleaseSerializer(serializers.ModelSerializer):
    tracks = serializers.HyperlinkedIdentityField(view_name='release-tracks')
    comments = serializers.HyperlinkedIdentityField(view_name='release-comments')

    class Meta:
        model = Release 
        fields = ('id', 'arrivaldate', 'artist',
                  'title', 'year','company','genre',
                  'format', 'local', 'cpa', 'compilation',
                  'female', 'tracks', 'comments','createwho',
                  'createwhen','copies','modifywho','modifywhen')
