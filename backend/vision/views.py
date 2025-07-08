import base64
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins, status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from authentication.authentication import APIKeyAuthentication

from .enums import OpenAIVisionModels
from .models import ChangeDetectionLog
from .serializers import (
    AnalysisRequestSerializer,
    ChangeDetectionLogSerializer,
)
from .services import get_change_description_from_llm


class ChangeDetectionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = [SessionAuthentication, APIKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return AnalysisRequestSerializer
        return ChangeDetectionLogSerializer

    def get_queryset(self):
        return ChangeDetectionLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        api_key = self.request.auth
        if not api_key:
            raise permissions.PermissionDenied("This endpoint can only be used with an API Key.")

        config = api_key.config

        model_to_use = serializer.validated_data.get("model") or config.default_model
        prompt_context_to_use = (
                serializer.validated_data.get("prompt_context") or config.prompt_context
        )

        log_instance = serializer.save(user=self.request.user, model_used=model_to_use)

        try:
            with open(log_instance.image1.path, "rb") as f:
                image1_base64 = base64.b64encode(f.read()).decode("utf-8")
            with open(log_instance.image2.path, "rb") as f:
                image2_base64 = base64.b64encode(f.read()).decode("utf-8")
        except (IOError, FileNotFoundError) as e:
            log_instance.delete()
            raise e

        description = get_change_description_from_llm(
            image1_base64, image2_base64, model_to_use, prompt_context_to_use
        )

        log_instance.description = description
        log_instance.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except (IOError, FileNotFoundError):
            return Response(
                {"error": "Could not read saved image files after upload."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except permissions.PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class AvailableModelsView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        models = [
            {"name": choice[0], "description": choice[1]}
            for choice in OpenAIVisionModels.choices
        ]
        return Response(models)


class LogReceiverView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        message = request.data.get("message")
        if message:
            user = request.user
            api_key_object = request.auth
            channel_layer = get_channel_layer()
            group_name = f"user_{user.id}_logs"
            log_payload = {
                "type": "log.message",
                "prefix": api_key_object.prefix,
                "message": message,
            }
            async_to_sync(channel_layer.group_send)(group_name, log_payload)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Message not provided"}, status=status.HTTP_400_BAD_REQUEST
        )


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "vision/dashboard.html"


class ProtectedMediaView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, log_id, image_field):
        log = get_object_or_404(ChangeDetectionLog, id=log_id)

        if log.user != request.user:
            raise PermissionDenied("You do not have permission to access this file.")

        image_file = None
        if image_field == 'image1' and log.image1:
            image_file = log.image1
        elif image_field == 'image2' and log.image2:
            image_file = log.image2
        else:
            raise Http404("Image not found.")

        try:
            with image_file.open('rb') as f:
                return HttpResponse(f.read(), content_type='image/jpeg')
        except IOError:
            raise Http404("Image file could not be opened.")

