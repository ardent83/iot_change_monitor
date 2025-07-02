from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChangeDetectionViewSet,
    DeviceConfigurationView,
    AvailableModelsView,
    LogReceiverView,
    LogViewerView
)

router = DefaultRouter()
router.register(r'logs', ChangeDetectionViewSet, basename='change-detection-log')

urlpatterns = [
    path('', include(router.urls)),
    path('config/', DeviceConfigurationView.as_view(), name='device-config'),
    path('models/', AvailableModelsView.as_view(), name='available-models'),

    path('log/', LogReceiverView.as_view(), name='log-receiver'),
    path('log-viewer/', LogViewerView.as_view(), name='log-viewer'),
]
