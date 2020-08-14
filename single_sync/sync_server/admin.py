from django.contrib import admin

from sync_server.models import AppRegister


@admin.register(AppRegister)
class AppRegisterAdmin(admin.ModelAdmin):
    fields = ['client_id', 'secret', 'client_host', 'active']
    list_display = ['client_id', 'client_host', 'active']
    list_filter = ['active']
