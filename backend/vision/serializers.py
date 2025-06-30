from rest_framework import serializers
from .models import ChangeDetectionLog, DeviceConfiguration
from .enums import OpenAIVisionModels


class ChangeDetectionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeDetectionLog
        fields = '__all__'


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
