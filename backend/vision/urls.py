from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChangeDetectionViewSet,
    AvailableModelsView,
    LogReceiverView,
)

router = DefaultRouter()
router.register(r'logs', ChangeDetectionViewSet, basename='change-detection-log')

urlpatterns = [
    path('', include(router.urls)),
    path('models/', AvailableModelsView.as_view(), name='available-models'),
    path('log/', LogReceiverView.as_view(), name='log-receiver'),
]
