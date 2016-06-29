from rest_framework import serializers
from .models import Release, Track, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'comment')

class TrackSerializer(serializers.ModelSerializer):
    cdid = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Track
        fields = ('trackid', 'tracknum', 'trackartist', 'tracktitle', 'tracklength', 'cdid')

class ReleaseSerializer(serializers.ModelSerializer):
    tracks = serializers.HyperlinkedIdentityField(view_name='release-tracks')
    comments = serializers.HyperlinkedIdentityField(view_name='release-comments')

    class Meta:
        model = Release 
        fields = ('id', 'arrivaldate', 'artist', 'title', 'year', 'local', 'cpa', 'compilation', 'female', 'tracks', 'comments')
