from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import UserAPIKey


class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key_header = request.META.get("HTTP_X_API_KEY")
        if not api_key_header:
            return None

        try:
            api_key = UserAPIKey.objects.get_from_key(api_key_header)
            user = api_key.user
        except UserAPIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API Key provided.')

        return user, api_key
