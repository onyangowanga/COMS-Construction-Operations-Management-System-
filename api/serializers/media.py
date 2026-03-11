"""
Media Serializers
Handles ProjectPhoto serialization
"""
from rest_framework import serializers
from apps.media.models import ProjectPhoto


class ProjectPhotoSerializer(serializers.ModelSerializer):
    """Serializer for ProjectPhoto model"""
    project_code = serializers.CharField(source='project.code', read_only=True)
    stage_name = serializers.CharField(source='stage.get_name_display', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = ProjectPhoto
        fields = [
            'id', 'project', 'project_code', 'stage', 'stage_name',
            'photo_path', 'caption', 'uploaded_by', 'uploaded_by_name',
            'uploaded_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uploaded_at', 'created_at', 'updated_at']


class ProjectPhotoListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for photo lists"""
    project_code = serializers.CharField(source='project.code', read_only=True)
    stage_name = serializers.CharField(source='stage.get_name_display', read_only=True)
    
    class Meta:
        model = ProjectPhoto
        fields = [
            'id', 'project', 'project_code', 'stage', 'stage_name',
            'photo_path', 'caption', 'uploaded_at'
        ]
