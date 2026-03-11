"""
BQ ViewSets
Handles BQSection, BQElement, BQItem API endpoints
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.bq.models import BQSection, BQElement, BQItem
from api.serializers.bq import (
    BQSectionSerializer, BQSectionListSerializer,
    BQElementSerializer, BQItemSerializer
)


class BQSectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BQSection model
    
    Provides CRUD operations for BQ sections
    """
    queryset = BQSection.objects.all().select_related('project').prefetch_related('elements__items')
    serializer_class = BQSectionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project']
    search_fields = ['name', 'description', 'project__code', 'project__name']
    ordering_fields = ['order', 'created_at']
    ordering = ['project', 'order']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return BQSectionListSerializer
        return BQSectionSerializer
    
    @action(detail=True, methods=['get'])
    def elements(self, request, pk=None):
        """Get all elements for a section"""
        section = self.get_object()
        elements = section.elements.all().order_by('order')
        serializer = BQElementSerializer(elements, many=True)
        return Response(serializer.data)


class BQElementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BQElement model
    
    Provides CRUD operations for BQ elements
    """
    queryset = BQElement.objects.all().select_related('section').prefetch_related('items')
    serializer_class = BQElementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['section', 'section__project']
    search_fields = ['name', 'description', 'section__name']
    ordering_fields = ['order', 'created_at']
    ordering = ['section', 'order']
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get all items for an element"""
        element = self.get_object()
        items = element.items.all()
        serializer = BQItemSerializer(items, many=True)
        return Response(serializer.data)


class BQItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BQItem model
    
    Provides CRUD operations for BQ items
    """
    queryset = BQItem.objects.all().select_related('element__section')
    serializer_class = BQItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['element', 'element__section', 'element__section__project']
    search_fields = ['description', 'element__name']
    ordering_fields = ['created_at']
    ordering = ['element', 'id']
