"""
Reporting Engine - API Serializers

DRF serializers for report management and execution.
"""

from rest_framework import serializers
from apps.reporting.models import Report, ReportSchedule, ReportExecution, ReportWidget
from apps.reporting.services import ReportService, ReportScheduleService


class UserBasicSerializer(serializers.Serializer):
    """Nested user serializer"""
    id = serializers.UUIDField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class ReportSerializer(serializers.ModelSerializer):
    """Full report serializer"""
    created_by = UserBasicSerializer(read_only=True)
    total_executions = serializers.ReadOnlyField()
    last_execution = serializers.ReadOnlyField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'code', 'year', 'sequence', 'organization', 'name', 'description', 'module',
            'report_type', 'filters', 'columns', 'aggregations', 'group_by',
            'default_parameters', 'is_active', 'is_public', 'cache_duration',
            'created_by', 'created_at', 'updated_at',
            'total_executions', 'last_execution'
        ]
        read_only_fields = ['id', 'code', 'year', 'sequence', 'organization', 'created_by', 'created_at', 'updated_at']


class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reports"""
    
    class Meta:
        model = Report
        fields = [
            'name', 'description', 'module', 'report_type',
            'filters', 'columns', 'aggregations', 'group_by', 'default_parameters',
            'is_public', 'cache_duration', 'code'
        ]
    
    def validate(self, data):
        """Validate that only superusers can manually set the code"""
        request = self.context.get('request')
        if 'code' in data and data['code']:
            # Check if user is superuser
            if not getattr(request.user, 'is_superuser', False):
                raise serializers.ValidationError(
                    {'code': 'Only admin users can manually set the report code.'}
                )
        return data
    
    def create(self, validated_data):
        request = self.context['request']
        return ReportService.create_report(
            organization=request.user.organization,
            created_by=request.user,
            **validated_data
        )


class ReportExecutionSerializer(serializers.ModelSerializer):
    """Serializer for report execution history"""
    report = ReportSerializer(read_only=True)
    executed_by = UserBasicSerializer(read_only=True)
    duration = serializers.ReadOnlyField()
    was_successful = serializers.ReadOnlyField()
    
    class Meta:
        model = ReportExecution
        fields = [
            'id', 'report', 'schedule', 'status', 'export_format',
            'parameters', 'file_path', 'file_size', 'row_count',
            'execution_time', 'error_message', 'cache_key',
            'executed_by', 'created_at', 'completed_at',
            'duration', 'was_successful'
        ]
        read_only_fields = fields


class ReportExecuteSerializer(serializers.Serializer):
    """Serializer for executing a report"""
    parameters = serializers.JSONField(required=False, default=dict)
    export_format = serializers.ChoiceField(
        choices=Report.ExportFormat.choices,
        default=Report.ExportFormat.PDF
    )
    use_cache = serializers.BooleanField(default=True)
    
    def execute(self, report, executed_by):
        """Execute the report"""
        return ReportService.generate_report(
            report=report,
            parameters=self.validated_data['parameters'],
            export_format=self.validated_data['export_format'],
            executed_by=executed_by,
            use_cache=self.validated_data['use_cache']
        )


class ReportScheduleSerializer(serializers.ModelSerializer):
    """Full schedule serializer"""
    report = ReportSerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    is_due = serializers.ReadOnlyField()
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'report', 'name', 'frequency', 'cron_expression',
            'export_format', 'parameters', 'delivery_method', 'recipients',
            'is_active', 'last_run', 'next_run', 'created_by',
            'created_at', 'updated_at', 'is_due'
        ]
        read_only_fields = ['id', 'report', 'last_run', 'next_run', 'created_by', 'created_at', 'updated_at']


class ReportScheduleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating schedules"""
    
    class Meta:
        model = ReportSchedule
        fields = [
            'name', 'frequency', 'cron_expression', 'export_format',
            'parameters', 'delivery_method', 'recipients'
        ]
    
    def create(self, validated_data):
        request = self.context['request']
        report_id = self.context['report_id']
        
        from apps.reporting.models import Report
        report = Report.objects.get(id=report_id)
        
        return ReportScheduleService.create_schedule(
            report=report,
            created_by=request.user,
            **validated_data
        )


class ReportWidgetSerializer(serializers.ModelSerializer):
    """Full widget serializer"""
    created_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = ReportWidget
        fields = [
            'id', 'organization', 'report', 'name', 'widget_type',
            'chart_type', 'data_source', 'query_parameters',
            'display_order', 'refresh_interval', 'icon', 'color',
            'is_active', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_by', 'created_at', 'updated_at']


class ReportWidgetDataSerializer(serializers.Serializer):
    """Serializer for widget data response"""
    value = serializers.Field()
    widget_type = serializers.CharField()
    chart_type = serializers.CharField()
    timestamp = serializers.DateTimeField()
    error = serializers.CharField(required=False)
