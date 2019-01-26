from django.contrib import admin

from .models import Comment

# Register your models here.
class CommentAdmin(admin.ModelAdmin):
    model = Comment
    exclude = ['release','cdtrackid']
    list_display = ['comment','author','visible']
    list_editable = ['visible']
    list_filter = ['author','visible']
    search_fields = ['comment']


admin.site.register(Comment, CommentAdmin)
