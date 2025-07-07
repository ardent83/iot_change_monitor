from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_api_key.models import APIKey


class UserRegisterSerializer(serializers.ModelSerializer):
    confirmPassword = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmPassword']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self):
        user = User(email=self.validated_data['email'], username=self.validated_data['username'])
        password = self.validated_data['password']
        confirmPassword = self.validated_data['confirmPassword']
        if password != confirmPassword:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


class APIKeySerializer(serializers.Serializer):
    prefix = serializers.CharField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    key = serializers.CharField(read_only=True)
