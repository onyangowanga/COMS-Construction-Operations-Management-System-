"""
Activity Service
Handles project activity logging
"""
from apps.workflows.models import ProjectActivity


def log_activity(
    project_id,
    activity_type,
    description,
    performed_by=None,
    amount=None,
    related_object_type=None,
    related_object_id=None,
    metadata=None
):
    """
    Log a project activity
    
    Args:
        project_id: UUID of the project
        activity_type: Activity type from ProjectActivity.ActivityType
        description: Text description of the activity
        performed_by: User who performed the activity
        amount: Optional monetary amount
        related_object_type: Type of related object (e.g., 'Expense', 'LPO')
        related_object_id: UUID of related object
        metadata: Additional metadata dict
    
    Returns:
        ProjectActivity instance
    """
    activity = ProjectActivity.objects.create(
        project_id=project_id,
        activity_type=activity_type,
        description=description,
        performed_by=performed_by,
        amount=amount,
        related_object_type=related_object_type or '',
        related_object_id=related_object_id,
        metadata=metadata or {}
    )
    
    return activity


def get_project_activity_timeline(project_id, limit=None):
    """
    Get activity timeline for a project
    
    Args:
        project_id: UUID of the project
        limit: Optional limit on number of activities
    
    Returns:
        QuerySet of ProjectActivity instances
    """
    activities = ProjectActivity.objects.filter(
        project_id=project_id
    ).select_related('performed_by').order_by('-created_at')
    
    if limit:
        activities = activities[:limit]
    
    return activities
