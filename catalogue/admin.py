from django.contrib import admin

from .models import Comment, Release


class ReleaseAdmin(admin.ModelAdmin):
    model: Release
    list_display = ['artist','title','ghoul_approved']
    search_fields = ['artist','title']
class CommentAdmin(admin.ModelAdmin):
    model = Comment
    exclude = ['release','cdtrackid']
    list_display = ['comment','author','visible']
    list_editable = ['visible']
    list_filter = ['author','visible']
    search_fields = ['comment']


admin.site.register(Comment, CommentAdmin)
admin.site.register(Release, ReleaseAdmin)
