"""
API URL Configuration
Main URL patterns for the REST API
"""
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from api.routers import router
from api.views.workflows import WorkflowStateAPIView, WorkflowTransitionAPIView
from api.views.exchange_rates import ExchangeRateView


urlpatterns = [
    # API Router - all CRUD endpoints
    path('', include(router.urls)),

    # Workflow Engine
    path('workflows/<str:module>/<uuid:entity_id>/', WorkflowStateAPIView.as_view(), name='workflow-state'),
    path('workflows/<str:module>/<uuid:entity_id>/transition/', WorkflowTransitionAPIView.as_view(), name='workflow-transition'),
    path('exchange-rates/', ExchangeRateView.as_view(), name='exchange-rates'),
    
    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
