from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from vision.views import DashboardView
from authentication.views import LoginTemplateView, RegisterTemplateView, UserGuideTemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('auth/login/', LoginTemplateView.as_view(), name='login-page'),
    path('auth/register/', RegisterTemplateView.as_view(), name='register-page'),
    path('auth/guide/', UserGuideTemplateView.as_view(), name='user-guide'),

    path('api/auth/', include('authentication.urls')),
    path('api/vision/', include('vision.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
