from django.contrib.auth import login, logout, authenticate
from django.views.generic import TemplateView
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.response import Response
from .models import UserAPIKey
from .serializers import UserRegisterSerializer, LoginSerializer, APIKeySerializer


class LoginTemplateView(TemplateView):
    template_name = "authentication/login.html"


class RegisterTemplateView(TemplateView):
    template_name = "authentication/register.html"


class UserGuideTemplateView(TemplateView):
    template_name = "authentication/user_guide.html"


class RegisterAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer


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


class LogoutAPIView(views.APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIKeyViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = APIKeySerializer

    def list(self, request):
        keys = UserAPIKey.objects.filter(user=request.user, revoked=False)
        data = [{'prefix': key.prefix, 'created': key.created, 'name': key.name} for key in keys]
        return Response(data)

    def create(self, request):
        name = request.data.get('name', 'esp32-device')
        api_key, key = UserAPIKey.objects.create_key(name=name, user=request.user)
        return Response({'prefix': api_key.prefix, 'key': key, 'name': name, 'created': api_key.created})

    def destroy(self, request, pk=None):
        try:
            key = UserAPIKey.objects.get(prefix=pk, user=request.user)
            key.revoked = True
            key.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserAPIKey.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
