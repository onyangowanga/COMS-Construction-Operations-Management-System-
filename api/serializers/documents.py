"""
Document Management System - API Serializers

Comprehensive serializers for document operations including:
- Document CRUD
- Version management
- Generic object linking
- File upload handling
"""

from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from apps.documents.models import Document
from apps.documents.services import DocumentService
from apps.documents.selectors import DocumentSelector


class UserBasicSerializer(serializers.Serializer):
    """Basic user info for nested serialization"""
    id = serializers.UUIDField()
    username = serializers.CharField()
    full_name = serializers.CharField(source='get_full_name')
    email = serializers.EmailField()


class ProjectBasicSerializer(serializers.Serializer):
    """Basic project info for nested serialization"""
    id = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()


class DocumentSerializer(serializers.ModelSerializer):
    """
    Full document serializer with all fields and nested data.
    
    Used for detail views and complete document information.
    """
    # Display fields
    document_type_display = serializers.CharField(
        source='get_document_type_display',
        read_only=True
    )
    
    # Nested data
    uploaded_by_data = UserBasicSerializer(source='uploaded_by', read_only=True)
    project_data = ProjectBasicSerializer(source='project', read_only=True)
    
    # File metadata
    file_name = serializers.CharField(read_only=True)
    file_size_display = serializers.CharField(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    # Computed properties
    is_image = serializers.BooleanField(read_only=True)
    is_pdf = serializers.BooleanField(read_only=True)
    is_cad = serializers.BooleanField(read_only=True)
    is_office_document = serializers.BooleanField(read_only=True)
    has_versions = serializers.BooleanField(read_only=True)
    
    # Digital signature
    is_signed = serializers.BooleanField(read_only=True)
    requires_signature = serializers.BooleanField(read_only=True)
    signed_by_data = UserBasicSerializer(source='signed_by', read_only=True)
    
    # Access control
    visibility_display = serializers.CharField(
        source='get_visibility_display',
        read_only=True
    )
    is_restricted = serializers.BooleanField(read_only=True)
    
    # Generic relation
    related_object_type = serializers.SerializerMethodField()
    related_object_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Document
        fields = [
            # Identification
            'id',
            'organization',
            'project',
            'project_data',
            'document_type',
            'document_type_display',
            'title',
            'description',
            
            # File
            'file',
            'file_name',
            'file_size',
            'file_size_mb',
            'file_size_display',
            'file_extension',
            'file_url',
            
            # File type checks
            'is_image',
            'is_pdf',
            'is_cad',
            'is_office_document',
            
            # Generic relation
            'content_type',
            'object_id',
            'related_object_type',
            'related_object_display',
            
            # Versioning
            'version',
            'is_latest',
            'previous_version',
            'version_notes',
            'has_versions',
            
            # Metadata
            'uploaded_by',
            'uploaded_by_data',
            'uploaded_at',
            'updated_at',
            
            # Additional
            'tags',
            'is_confidential',
            'expiry_date',
            'reference_number',
            
            # Digital signature
            'signed_by',
            'signed_by_data',
            'signed_at',
            'signature_hash',
            'is_signed',
            'requires_signature',
            
            # Access control
            'visibility',
            'visibility_display',
            'is_restricted',
        ]
        read_only_fields = [
            'id',
            'file_size',
            'file_extension',
            'uploaded_at',
            'updated_at',
            'version',
            'signed_at',
            'signature_hash',
        ]
    
    def get_file_url(self, obj):
        """Get download URL for file"""
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_related_object_type(self, obj):
        """Get human-readable related object type"""
        if obj.content_type:
            return obj.content_type.model
        return None


class DocumentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for document lists.
    
    Optimized for list views with minimal data.
    """
    document_type_display = serializers.CharField(
        source='get_document_type_display',
        read_only=True
    )
    project_code = serializers.CharField(source='project.code', read_only=True)
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.get_full_name',
        read_only=True
    )
    file_size_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'document_type',
            'document_type_display',
            'project',
            'project_code',
            'file_name',
            'file_size_display',
            'file_extension',
            'version',
            'is_latest',
            'is_confidential',
            'uploaded_by_name',
            'uploaded_at',
        ]


class DocumentUploadSerializer(serializers.Serializer):
    """
    Serializer for uploading new documents.
    
    Handles file upload and metadata creation.
    """
    title = serializers.CharField(max_length=255)
    document_type = serializers.ChoiceField(choices=Document.DocumentType.choices)
    file = serializers.FileField()
    project = serializers.UUIDField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    tags = serializers.CharField(required=False, allow_blank=True, default='')
    is_confidential = serializers.BooleanField(default=False)
    reference_number = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
        default=''
    )
    expiry_date = serializers.DateField(required=False, allow_null=True)
    visibility = serializers.ChoiceField(
        choices=Document.Visibility.choices,
        default=Document.Visibility.PROJECT_TEAM,
        required=False
    )
    
    # Generic relation fields
    related_object_type = serializers.CharField(required=False, allow_blank=True)
    related_object_id = serializers.UUIDField(required=False, allow_null=True)
    
    def create(self, validated_data):
        """Create document using service layer"""
        from apps.projects.models import Project
        
        # Get request user
        user = self.context['request'].user
        organization = user.organization
        
        # Get project if provided
        project = None
        if validated_data.get('project'):
            try:
                project = Project.objects.get(id=validated_data['project'])
            except Project.DoesNotExist:
                raise serializers.ValidationError("Project not found")
        
        # Get related object if provided
        related_object = None
        if validated_data.get('related_object_type') and validated_data.get('related_object_id'):
            try:
                content_type = ContentType.objects.get(
                    model=validated_data['related_object_type'].lower()
                )
                model_class = content_type.model_class()
                related_object = model_class.objects.get(
                    id=validated_data['related_object_id']
                )
            except (ContentType.DoesNotExist, model_class.DoesNotExist):
                raise serializers.ValidationError("Related object not found")
        
        # Create document
        document = DocumentService.upload_document(
            title=validated_data['title'],
            document_type=validated_data['document_type'],
            file=validated_data['file'],
            uploaded_by=user,
            project=project,
            organization=organization,
            description=validated_data.get('description', ''),
            tags=validated_data.get('tags', ''),
            is_confidential=validated_data.get('is_confidential', False),
            reference_number=validated_data.get('reference_number', ''),
            expiry_date=validated_data.get('expiry_date'),
            related_object=related_object,
            visibility=validated_data.get('visibility', Document.Visibility.PROJECT_TEAM)
        )
        
        return document


class DocumentVersionSerializer(serializers.Serializer):
    """
    Serializer for creating new document versions.
    
    Handles version creation with new file upload.
    """
    file = serializers.FileField()
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    
    def create(self, validated_data):
        """Create new version using service layer"""
        document_id = self.context.get('document_id')
        user = self.context['request'].user
        
        # Get original document
        try:
            original_document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            raise serializers.ValidationError("Document not found")
        
        # Create new version
        new_version = DocumentService.create_new_version(
            document=original_document,
            new_file=validated_data['file'],
            uploaded_by=user,
            notes=validated_data.get('notes', '')
        )
        
        return new_version


class DocumentUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating document metadata.
    
    Does not change the file, only metadata.
    """
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.CharField(required=False, allow_blank=True)
    is_confidential = serializers.BooleanField(required=False)
    reference_number = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100
    )
    expiry_date = serializers.DateField(required=False, allow_null=True)
    
    def update(self, instance, validated_data):
        """Update document using service layer"""
        updated_document = DocumentService.update_document_metadata(
            document=instance,
            title=validated_data.get('title'),
            description=validated_data.get('description'),
            tags=validated_data.get('tags'),
            is_confidential=validated_data.get('is_confidential'),
            reference_number=validated_data.get('reference_number'),
            expiry_date=validated_data.get('expiry_date')
        )
        
        return updated_document


class DocumentStatsSerializer(serializers.Serializer):
    """Serializer for document statistics"""
    total_documents = serializers.IntegerField()
    total_size_bytes = serializers.IntegerField()
    total_size_mb = serializers.FloatField()
    counts_by_type = serializers.DictField()
    confidential_count = serializers.IntegerField()


class DocumentSignSerializer(serializers.Serializer):
    """
    Serializer for digitally signing a document.
    
    Creates a cryptographic signature hash.
    """
    signature_text = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional signature text to include in hash"
    )
    
    def update(self, instance, validated_data):
        """Sign document using service layer"""
        user = self.context.get('request').user
        
        signed_document = DocumentService.sign_document(
            document=instance,
            signed_by=user,
            signature_text=validated_data.get('signature_text')
        )
        
        return signed_document


class DocumentVisibilitySerializer(serializers.Serializer):
    """
    Serializer for updating document visibility/access control.
    """
    visibility = serializers.ChoiceField(
        choices=Document.Visibility.choices,
        help_text="Document visibility level"
    )
    
    def validate_visibility(self, value):
        """Validate visibility choice"""
        if value not in Document.Visibility.values:
            raise serializers.ValidationError(f"Invalid visibility level: {value}")
        return value
    
    def update(self, instance, validated_data):
        """Update visibility using service layer"""
        user = self.context.get('request').user
        
        updated_document = DocumentService.update_visibility(
            document=instance,
            visibility=validated_data['visibility'],
            updated_by=user
        )
        
        return updated_document

