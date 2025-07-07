from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'keys', views.APIKeyViewSet, basename='api-key')

urlpatterns = [
    # Page serving URLs
    path('login/', views.LoginTemplateView.as_view(), name='login-page'),
    path('register/', views.RegisterTemplateView.as_view(), name='register-page'),
    path('guide/', views.UserGuideTemplateView.as_view(), name='user-guide'),

    # API endpoint URLs
    path('api/register/', views.RegisterAPIView.as_view(), name='api-register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api-login'),
    path('api/logout/', views.LogoutAPIView.as_view(), name='api-logout'),
    path('api/', include(router.urls)),
]
