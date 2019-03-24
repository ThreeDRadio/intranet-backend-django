from rest_framework import serializers
from .models import Release, Track, Comment
from django.contrib.auth.models import User 
import urllib, hashlib

class ProfileSerializer(serializers.ModelSerializer):
    gravatar = serializers.SerializerMethodField('getGravatar')

    def getGravatar(self, obj):
        name = obj.email if obj.email else obj.username
        gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(name.lower().encode('utf-8')).hexdigest()
        return gravatar_url

    
    class Meta:
        model = User
        fields = ('first_name','last_name','gravatar','id')

class EmbeddedReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release 
        fields = ('id', 'artist', 'title')

class CommentSerializer(serializers.ModelSerializer):
    author = ProfileSerializer()
    release = EmbeddedReleaseSerializer()
    class Meta:
        model = Comment
        fields = ('id', 'comment','author','createwhen','release')

class TrackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Track
        fields = ('id','release', 'tracknum', 'trackartist', 'tracktitle', 'tracklength', 'release', 'hiAvailable','needsencoding')

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
