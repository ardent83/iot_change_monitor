from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserAPIKey
from vision.models import DeviceConfiguration


@receiver(post_save, sender=UserAPIKey)
def create_device_configuration(sender, instance, created, **kwargs):
    if created:
        DeviceConfiguration.objects.create(api_key=instance)
