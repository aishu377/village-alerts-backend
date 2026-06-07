from django.contrib import admin
from .models import Alert, UserDevice


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'severity', 'village', 'district', 'is_active', 'created_at']
    list_filter = ['category', 'severity', 'is_active', 'state']
    search_fields = ['title', 'village', 'district', 'message']
    list_editable = ['is_active']
    ordering = ['-created_at']


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ['village', 'district', 'state', 'updated_at']
    search_fields = ['village', 'district']
