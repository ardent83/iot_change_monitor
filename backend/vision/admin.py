from django.contrib import admin
from .models import ChangeDetectionLog, DeviceConfiguration


@admin.register(ChangeDetectionLog)
class ChangeDetectionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'model_used', 'created_at', 'description')
    readonly_fields = ('image1', 'image2', 'description', 'created_at', 'model_used')


@admin.register(DeviceConfiguration)
class DeviceConfigurationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'default_model', 'delay_seconds', 'flash_enabled', 'updated_at')
