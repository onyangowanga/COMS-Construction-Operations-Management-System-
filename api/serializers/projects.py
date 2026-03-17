"""
Project Serializers
Handles Project and ProjectStage serialization
"""
from rest_framework import serializers
from apps.projects.models import Project, ProjectStage


class ProjectStageSerializer(serializers.ModelSerializer):
    """Serializer for ProjectStage model"""
    name_display = serializers.CharField(source='get_name_display', read_only=True)
    
    class Meta:
        model = ProjectStage
        fields = [
            'id', 'project', 'name', 'name_display', 'description', 
            'order', 'start_date', 'end_date', 'is_completed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
    project_type_display = serializers.CharField(source='get_project_type_display', read_only=True)
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    stages = ProjectStageSerializer(many=True, read_only=True)
    
    # Computed fields
    total_stages = serializers.SerializerMethodField()
    completed_stages = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'organization', 'code', 'name', 'client_name', 
            'location', 'project_type', 'project_type_display',
            'contract_type', 'contract_type_display', 'project_value',
            'start_date', 'end_date', 'status', 'status_display',
            'description', 'stages', 'total_stages', 'completed_stages',
            'progress_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'code': {'required': False},
        }
    
    def get_total_stages(self, obj):
        """Get total number of stages"""
        return obj.stages.count()
    
    def get_completed_stages(self, obj):
        """Get number of completed stages"""
        return obj.stages.filter(is_completed=True).count()
    
    def get_progress_percentage(self, obj):
        """Calculate project progress percentage"""
        total = obj.stages.count()
        if total == 0:
            return 0
        completed = obj.stages.filter(is_completed=True).count()
        return round((completed / total) * 100, 2)


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for project lists"""
    project_type_display = serializers.CharField(source='get_project_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'code', 'name', 'client_name', 'project_type',
            'project_type_display', 'status', 'status_display',
            'project_value', 'start_date', 'progress_percentage'
        ]
    
    def get_progress_percentage(self, obj):
        """Calculate project progress percentage"""
        total = obj.stages.count()
        if total == 0:
            return 0
        completed = obj.stages.filter(is_completed=True).count()
        return round((completed / total) * 100, 2)
