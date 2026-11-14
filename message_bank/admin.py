from django.contrib import admin

from message_bank.models import Message, MessageType

# Register your models here.
class MessageAdmin(admin.ModelAdmin):
    ordering = ("-created",)
    list_display = ("code", "title", "expirydate", "created")
    
class MessageTypeAdmin(admin.ModelAdmin):
    ordering = ("type",)
    list_display = ("type", "description")

admin.site.register(Message, MessageAdmin)
admin.site.register(MessageType, MessageTypeAdmin)