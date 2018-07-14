from django.contrib import admin

from .models import Whitelist

# Register your models here.


class WhitelistAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip']
    model = Whitelist


admin.site.register(Whitelist, WhitelistAdmin)
