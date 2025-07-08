from rest_framework import serializers
from .models import ChangeDetectionLog, DeviceConfiguration
from .enums import OpenAIVisionModels


class ChangeDetectionLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ChangeDetectionLog
        fields = ['id', 'user', 'image1', 'image2', 'model_used', 'description', 'created_at']
        read_only_fields = ['id', 'user', 'description', 'created_at']


class AnalysisRequestSerializer(serializers.Serializer):
    image1 = serializers.ImageField(required=True)
    image2 = serializers.ImageField(required=True)
    model = serializers.ChoiceField(choices=OpenAIVisionModels.choices, required=False, allow_blank=True)
    prompt_context = serializers.CharField(required=False, allow_blank=True)


class DeviceConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceConfiguration
        fields = ['flash_enabled', 'delay_seconds', 'default_model', 'prompt_context', 'updated_at']
        read_only_fields = ['updated_at']


class ESP32ImageUploadSerializer(serializers.Serializer):
    """
    A very simple serializer to validate that two images are uploaded.
    This is specifically for the ESP32 endpoint.
    """
    image1 = serializers.ImageField(required=True)
    image2 = serializers.ImageField(required=True)
