"""
BQ (Bill of Quantities) Serializers
Handles BQSection, BQElement, BQItem serialization
"""
from rest_framework import serializers
from apps.bq.models import BQSection, BQElement, BQItem


class BQItemSerializer(serializers.ModelSerializer):
    """Serializer for BQItem model"""
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = BQItem
        fields = [
            'id', 'element', 'description', 'quantity', 'unit',
            'rate', 'total_amount', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Calculate total_amount on save"""
        if 'quantity' in data and 'rate' in data:
            data['total_amount'] = data['quantity'] * data['rate']
        return data


class BQElementSerializer(serializers.ModelSerializer):
    """Serializer for BQElement model"""
    items = BQItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BQElement
        fields = [
            'id', 'section', 'name', 'description', 'order',
            'items', 'item_count', 'total_amount',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_amount(self, obj):
        """Calculate total amount for all items in this element"""
        return sum(item.total_amount for item in obj.items.all())
    
    def get_item_count(self, obj):
        """Get number of items in this element"""
        return obj.items.count()


class BQSectionSerializer(serializers.ModelSerializer):
    """Serializer for BQSection model"""
    elements = BQElementSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    element_count = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BQSection
        fields = [
            'id', 'project', 'name', 'description', 'order',
            'elements', 'element_count', 'item_count', 'total_amount',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_amount(self, obj):
        """Calculate total amount for all elements in this section"""
        total = 0
        for element in obj.elements.all():
            total += sum(item.total_amount for item in element.items.all())
        return total
    
    def get_element_count(self, obj):
        """Get number of elements in this section"""
        return obj.elements.count()
    
    def get_item_count(self, obj):
        """Get total number of items across all elements"""
        return sum(element.items.count() for element in obj.elements.all())


class BQSectionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for BQ section lists"""
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = BQSection
        fields = ['id', 'project', 'name', 'order', 'total_amount']
    
    def get_total_amount(self, obj):
        """Calculate total amount"""
        total = 0
        for element in obj.elements.all():
            total += sum(item.total_amount for item in element.items.all())
        return total
