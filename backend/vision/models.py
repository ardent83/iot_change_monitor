from django.db import models
from django.conf import settings
import uuid
from .enums import OpenAIVisionModels


class ChangeDetectionLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name="User"
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image1 = models.ImageField(upload_to='change_detection/', verbose_name="First Image")
    image2 = models.ImageField(upload_to='change_detection/', verbose_name="Second Image")
    model_used = models.CharField(max_length=50, blank=True, verbose_name="AI Model Used")
    description = models.TextField(blank=True, null=True, verbose_name="Change Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creation Time")

    class Meta:
        verbose_name = "Change Detection Log"
        verbose_name_plural = "Change Detection Logs"
        ordering = ['-created_at']


class DeviceConfiguration(models.Model):
    api_key = models.OneToOneField(
        "authentication.UserAPIKey",
        on_delete=models.CASCADE,
        related_name="config",
        verbose_name="API Key"
    )
    flash_enabled = models.BooleanField(default=True, verbose_name="Enable ESP32 Flash")
    delay_seconds = models.PositiveIntegerField(default=10, verbose_name="Delay Between Photos (seconds)")
    default_model = models.CharField(
        max_length=50,
        choices=OpenAIVisionModels.choices,
        default=OpenAIVisionModels.GPT_4o_MINI,
        verbose_name="Default AI Model"
    )
    prompt_context = models.TextField(
        blank=True,
        verbose_name="Custom Prompt Context",
        help_text="Describe specific concerns, e.g., 'check for fire hazards' or 'monitor for unauthorized access'."
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuration for {self.api_key.name}"

    class Meta:
        verbose_name = "Device Configuration"
        verbose_name_plural = "Device Configurations"
