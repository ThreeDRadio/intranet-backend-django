from django.contrib import admin

from .models import Supporter, SupporterNote, Transaction

# Register your models here.
class SupporterAdmin(admin.ModelAdmin):
    model = Supporter 
    list_display = ['last_name','first_name','address1','address2','town','phone_mobile','email']
    search_fields = ['last_name','id']

class SupporterNoteAdmin(admin.ModelAdmin):
    model = SupporterNote

class TransactionAdmin(admin.ModelAdmin):
    model = Transaction

admin.site.register(Supporter, SupporterAdmin)
admin.site.register(SupporterNote, SupporterNoteAdmin)
admin.site.register(Transaction, TransactionAdmin)
