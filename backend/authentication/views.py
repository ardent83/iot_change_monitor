from django.contrib.auth import login, logout, authenticate
from django.views.generic import TemplateView
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import UserAPIKey
from .serializers import UserRegisterSerializer, LoginSerializer, APIKeySerializer
from vision.serializers import DeviceConfigurationSerializer
from vision.models import DeviceConfiguration


class LoginTemplateView(TemplateView):
    template_name = "authentication/login.html"


class RegisterTemplateView(TemplateView):
    template_name = "authentication/register.html"


class UserGuideTemplateView(TemplateView):
    template_name = "authentication/user_guide.html"


@extend_schema(summary="Register a New User")
class RegisterAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer


@extend_schema(
    summary="User Login (Sets Session Cookie)",
    request=LoginSerializer,
    responses={200: {"description": "Login successful."}}
)
class LoginAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Login was successful."}, status=status.HTTP_200_OK)
        return Response({'error': 'The username or password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(summary="User Logout (Clears Session)", request=None, responses={204: None})
class LogoutAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIKeyViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = APIKeySerializer
    queryset = UserAPIKey.objects.none()

    def get_serializer_class(self):
        if self.action == "config":
            return DeviceConfigurationSerializer
        return APIKeySerializer

    @extend_schema(summary="List User's API Keys", responses=APIKeySerializer(many=True))
    def list(self, request):
        keys = UserAPIKey.objects.filter(user=request.user, revoked=False)
        data = [{'prefix': key.prefix, 'created': key.created, 'name': key.name} for key in keys]
        return Response(data)

    @extend_schema(summary="Create a New API Key", responses={201: APIKeySerializer})
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data.get('name', 'esp32-device')

        api_key, key = UserAPIKey.objects.create_key(name=name, user=request.user)
        return Response({'prefix': api_key.prefix, 'key': key, 'name': name, 'created': api_key.created})

    @extend_schema(
        summary="Delete an API Key",
        parameters=[
            OpenApiParameter(name='pk', description='The prefix of the API Key to delete.', required=True, type=str,
                             location=OpenApiParameter.PATH)
        ],
        request=None,
        responses={204: None}
    )
    def destroy(self, request, pk=None):
        try:
            key = UserAPIKey.objects.get(prefix=pk, user=request.user)
            key.revoked = True
            key.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserAPIKey.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Configuration for a Specific API Key",
        parameters=[
            OpenApiParameter(name='pk', description='The prefix of the API Key.', required=True, type=str,
                             location=OpenApiParameter.PATH)
        ],
        request=DeviceConfigurationSerializer,
        responses={200: DeviceConfigurationSerializer}
    )
    @action(detail=True, methods=['get', 'patch'], url_path='config')
    def config(self, request, pk=None):
        api_key = None
        try:
            api_key = UserAPIKey.objects.get(prefix=pk, user=request.user)
            config_instance = api_key.config
        except UserAPIKey.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except DeviceConfiguration.DoesNotExist:
            config_instance = DeviceConfiguration.objects.create(api_key=api_key)

        if request.method == 'GET':
            serializer = DeviceConfigurationSerializer(config_instance)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = DeviceConfigurationSerializer(config_instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
