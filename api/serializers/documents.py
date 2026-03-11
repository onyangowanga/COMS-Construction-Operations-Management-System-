"""
Document Serializers
Handles Document and DocumentVersion serialization
"""
from rest_framework import serializers
from apps.documents.models import Document, DocumentVersion


class DocumentVersionSerializer(serializers.ModelSerializer):
    """Serializer for DocumentVersion model"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = DocumentVersion
        fields = [
            'id', 'document', 'version_number', 'file_path',
            'is_latest', 'uploaded_by', 'uploaded_by_name',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    versions = DocumentVersionSerializer(many=True, read_only=True)
    latest_version = serializers.SerializerMethodField()
    version_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'project', 'project_code', 'name', 'document_type',
            'document_type_display', 'uploaded_by', 'uploaded_by_name',
            'description', 'versions', 'latest_version', 'version_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_latest_version(self, obj):
        """Get the latest version"""
        latest = obj.latest_version
        if latest:
            return DocumentVersionSerializer(latest).data
        return None
    
    def get_version_count(self, obj):
        """Get number of versions"""
        return obj.versions.count()


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for document lists"""
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'project', 'project_code', 'name',
            'document_type', 'document_type_display', 'created_at'
        ]
