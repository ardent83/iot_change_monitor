import base64
from rest_framework import viewsets, mixins, status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.generic import TemplateView
from drf_spectacular.utils import extend_schema
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import ChangeDetectionLog, DeviceConfiguration
from .enums import OpenAIVisionModels
from .serializers import (
    ChangeDetectionLogSerializer,
    AnalysisRequestSerializer,
    DeviceConfigurationSerializer,
)
from .services import get_change_description_from_llm

from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey
from authentication.models import UserAPIKey


class HasUserAPIKey(HasAPIKey):
    model = UserAPIKey


class ChangeDetectionViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.CreateModelMixin,
                             viewsets.GenericViewSet):
    permission_classes = [HasUserAPIKey | IsAuthenticated]
    queryset = ChangeDetectionLog.objects.all()

    def get_queryset(self):
        user = self.request.user
        return ChangeDetectionLog.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return AnalysisRequestSerializer
        return ChangeDetectionLogSerializer

    @extend_schema(
        summary="Analyze Image Differences",
        description="Upload two images to get an AI-generated description of the differences. You can optionally "
                    "specify a model and custom prompt context.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image1': {'type': 'string', 'format': 'binary'},
                    'image2': {'type': 'string', 'format': 'binary'},
                    'model': {'type': 'string', 'enum': [choice[0] for choice in OpenAIVisionModels.choices]},
                    'prompt_context': {'type': 'string'}
                },
                'required': ['image1', 'image2']
            }
        },
        responses={201: ChangeDetectionLogSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        device_config, _ = DeviceConfiguration.objects.get_or_create(pk=1)

        model_to_use = validated_data.get('model') or device_config.default_model
        prompt_context_to_use = validated_data.get('prompt_context') or device_config.prompt_context

        log_instance = ChangeDetectionLog.objects.create(
            user=request.user,
            image1=validated_data['image1'],
            image2=validated_data['image2'],
            model_used=model_to_use
        )

        try:
            with open(log_instance.image1.path, "rb") as f:
                image1_base64 = base64.b64encode(f.read()).decode('utf-8')
            with open(log_instance.image2.path, "rb") as f:
                image2_base64 = base64.b64encode(f.read()).decode('utf-8')
        except (IOError, FileNotFoundError) as e:
            log_instance.delete()
            return Response({"error": f"Could not read saved image files: {e}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        description = get_change_description_from_llm(image1_base64, image2_base64, model_to_use, prompt_context_to_use)

        log_instance.description = description
        log_instance.save()

        final_serializer = ChangeDetectionLogSerializer(log_instance)
        return Response(final_serializer.data, status=status.HTTP_201_CREATED)


class AvailableModelsView(generics.GenericAPIView):
    """
    Get a list of available OpenAI vision models for analysis.
    """
    serializer_class = None

    def get(self, request, *args, **kwargs):
        models = [{"name": choice[0], "description": choice[1]} for choice in OpenAIVisionModels.choices]
        return Response(models)


class LogReceiverView(APIView):
    permission_classes = [HasUserAPIKey]

    def post(self, request, *args, **kwargs):
        message = request.data.get('message')
        if message:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'esp32_log_group',
                {
                    'type': 'log.message',
                    'message': message
                }
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Message not provided'}, status=status.HTTP_400_BAD_REQUEST)


class DashboardView(TemplateView):
    """
    Serves the main HTML dashboard page.
    """
    template_name = 'vision/dashboard.html'
