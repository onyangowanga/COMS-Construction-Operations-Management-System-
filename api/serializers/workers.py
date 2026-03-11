"""
Worker Serializers
Handles Worker and DailyLabourRecord serialization
"""
from rest_framework import serializers
from apps.workers.models import Worker, DailyLabourRecord


class DailyLabourRecordSerializer(serializers.ModelSerializer):
    """Serializer for DailyLabourRecord model"""
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    total_wage = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyLabourRecord
        fields = [
            'id', 'project', 'project_code', 'worker', 'worker_name',
            'date', 'daily_wage', 'hours_worked', 'total_wage',
            'paid', 'payment_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_wage(self, obj):
        """Calculate total wage (could be enhanced with overtime logic)"""
        return obj.daily_wage


class WorkerSerializer(serializers.ModelSerializer):
    """Serializer for Worker model"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    daily_records = DailyLabourRecordSerializer(many=True, read_only=True)
    total_days_worked = serializers.SerializerMethodField()
    total_wages_earned = serializers.SerializerMethodField()
    total_unpaid = serializers.SerializerMethodField()
    
    class Meta:
        model = Worker
        fields = [
            'id', 'organization', 'name', 'phone', 'id_number',
            'role', 'role_display', 'default_daily_wage', 'is_active',
            'daily_records', 'total_days_worked', 'total_wages_earned',
            'total_unpaid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_days_worked(self, obj):
        """Get total number of records"""
        return obj.daily_records.count()
    
    def get_total_wages_earned(self, obj):
        """Calculate total wages across all records"""
        return sum(record.daily_wage for record in obj.daily_records.all())
    
    def get_total_unpaid(self, obj):
        """Calculate total unpaid wages"""
        return sum(
            record.daily_wage 
            for record in obj.daily_records.filter(paid=False)
        )


class WorkerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for worker lists"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = Worker
        fields = [
            'id', 'name', 'role', 'role_display', 'phone',
            'default_daily_wage', 'is_active'
        ]
