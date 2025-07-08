from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api-keys', views.APIKeyViewSet, basename='api-key')

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='api-register'),
    path('login/', views.LoginAPIView.as_view(), name='api-login'),
    path('logout/', views.LogoutAPIView.as_view(), name='api-logout'),
    path('', include(router.urls)),
]
