from django.contrib import admin

import models

# Register your models here.
class CommentAdmin(admin.ModelAdmin):
    model = models.Comment


admin.site.register(models.Comment, CommentAdmin)
