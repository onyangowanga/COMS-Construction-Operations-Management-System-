"""
Reporting Engine - Celery Tasks

Background tasks for scheduled report execution and cleanup.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from apps.reporting.services import ReportScheduleService
from apps.reporting.models import ReportExecution


@shared_task(name='reporting.execute_scheduled_reports')
def execute_scheduled_reports():
    """
    Execute all due scheduled reports.
    
    This task should be run periodically (e.g., every 5-15 minutes).
    """
    try:
        ReportScheduleService.execute_due_schedules()
        return {'status': 'success', 'message': 'Scheduled reports executed'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@shared_task(name='reporting.cleanup_old_executions')
def cleanup_old_executions(days=90):
    """
    Clean up old report executions.
    
    Args:
        days: Number of days to retain executions (default: 90)
    
    This task should be run daily to remove old execution records
    and free up storage space.
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # Get old executions
    old_executions = ReportExecution.objects.filter(
        created_at__lt=cutoff_date
    )
    
    count = old_executions.count()
    
    # Delete files and records
    import os
    from django.conf import settings
    
    for execution in old_executions:
        if execution.file_path:
            file_path = os.path.join(settings.MEDIA_ROOT, execution.file_path)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass  # File already deleted or inaccessible
    
    # Delete execution records
    old_executions.delete()
    
    return {
        'status': 'success',
        'message': f'Cleaned up {count} old executions'
    }


@shared_task(name='reporting.cleanup_failed_executions')
def cleanup_failed_executions(hours=24):
    """
    Clean up failed executions after specified hours.
    
    Args:
        hours: Number of hours to retain failed executions (default: 24)
    """
    cutoff_date = timezone.now() - timedelta(hours=hours)
    
    failed_executions = ReportExecution.objects.filter(
        status=ReportExecution.Status.FAILED,
        created_at__lt=cutoff_date
    )
    
    count = failed_executions.count()
    
    # Delete files associated with failed executions
    import os
    from django.conf import settings
    
    for execution in failed_executions:
        if execution.file_path:
            file_path = os.path.join(settings.MEDIA_ROOT, execution.file_path)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
    
    # Delete failed execution records
    failed_executions.delete()
    
    return {
        'status': 'success',
        'message': f'Cleaned up {count} failed executions'
    }
