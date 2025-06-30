from django.db import models
import uuid
from .enums import OpenAIVisionModels


class ChangeDetectionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image1 = models.ImageField(upload_to='change_detection/', verbose_name="First Image")
    image2 = models.ImageField(upload_to='change_detection/', verbose_name="Second Image")
    model_used = models.CharField(max_length=50, blank=True, verbose_name="AI Model Used")
    description = models.TextField(blank=True, null=True, verbose_name="Change Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creation Time")

    def __str__(self):
        return f"Analysis at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Change Detection Log"
        verbose_name_plural = "Change Detection Logs"
        ordering = ['-created_at']


class DeviceConfiguration(models.Model):
    # This model uses a singleton pattern to ensure only one configuration object exists.
    id = models.IntegerField(primary_key=True, default=1, editable=False)
    flash_enabled = models.BooleanField(default=True, verbose_name="Enable ESP32 Flash")
    delay_seconds = models.PositiveIntegerField(default=10, verbose_name="Delay Between Photos (seconds)")
    default_model = models.CharField(
        max_length=50,
        choices=OpenAIVisionModels.choices,
        default=OpenAIVisionModels.GPT_4_1_MINI,
        verbose_name="Default AI Model"
    )
    prompt_context = models.TextField(
        blank=True,
        verbose_name="Custom Prompt Context",
        help_text="Describe specific concerns, e.g., 'check for fire hazards' or 'monitor for unauthorized access'."
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "System & Device Configuration"

    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"
