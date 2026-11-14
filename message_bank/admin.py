from django.contrib import admin

from message_bank.models import Message, MessageType, Program


# Register your models here.
class MessageAdmin(admin.ModelAdmin):
    ordering = ("-created",)
    list_display = ("code", "title", "expirydate", "created")


class MessageTypeAdmin(admin.ModelAdmin):
    ordering = ("type",)
    list_display = ("type", "description")


class ProgramAdmin(admin.ModelAdmin):
    ordering = ("-day","start")
    list_display = ("code", "name", "day", "start", "presenters", "description")

admin.site.register(Message, MessageAdmin)
admin.site.register(MessageType, MessageTypeAdmin)
admin.site.register(Program, ProgramAdmin)
