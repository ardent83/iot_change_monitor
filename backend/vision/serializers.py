from rest_framework import serializers
from django.urls import reverse
from .models import ChangeDetectionLog, DeviceConfiguration
from .enums import OpenAIVisionModels


class ChangeDetectionLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    image1_url = serializers.SerializerMethodField()
    image2_url = serializers.SerializerMethodField()

    class Meta:
        model = ChangeDetectionLog
        fields = [
            'id', 'user', 'model_used', 'description', 'created_at',
            'image1_url', 'image2_url'
        ]

    def get_image1_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(
            reverse('protected-media', kwargs={'log_id': obj.id, 'image_field': 'image1'})
        )

    def get_image2_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(
            reverse('protected-media', kwargs={'log_id': obj.id, 'image_field': 'image2'})
        )


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
