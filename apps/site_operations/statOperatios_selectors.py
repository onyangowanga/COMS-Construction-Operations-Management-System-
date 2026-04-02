"""
Site Operations Selectors

Query functions for retrieving site operations data.
All database queries should go through selectors to maintain
separation of concerns and enable query optimization.
"""

from typing import List, Dict, Any, Optional
from datetime import date, timedelta
from django.db import models
from django.db.models import Count, Q, Prefetch, Max, Min

from apps.site_operations.models import (
    DailySiteReport,
    MaterialDelivery,
    SiteIssue
)


def get_project_site_reports(
    project_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> models.QuerySet:
    """
    Get all site reports for a project with related data
    
    Args:
        project_id: UUID of the project
        start_date: Filter reports from this date onwards (optional)
        end_date: Filter reports up to this date (optional)
    
    Returns:
        QuerySet of DailySiteReport objects
    """
    queryset = DailySiteReport.objects.filter(
        project_id=project_id
    ).select_related(
        'project',
        'prepared_by'
    ).order_by('-report_date', '-created_at')
    
    if start_date:
        queryset = queryset.filter(report_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(report_date__lte=end_date)
    
    return queryset


def get_site_report_by_id(report_id: str) -> Optional[DailySiteReport]:
    """
    Get a specific site report by ID with all related data
    
    Args:
        report_id: UUID of the report
    
    Returns:
        DailySiteReport instance or None
    """
    try:
        return DailySiteReport.objects.select_related(
            'project',
            'prepared_by'
        ).get(id=report_id)
    except DailySiteReport.DoesNotExist:
        return None


def get_latest_site_report(project_id: str) -> Optional[DailySiteReport]:
    """
    Get the most recent site report for a project
    
    Args:
        project_id: UUID of the project
    
    Returns:
        Latest DailySiteReport or None
    """
    return DailySiteReport.objects.filter(
        project_id=project_id
    ).select_related(
        'project',
        'prepared_by'
    ).order_by('-report_date', '-created_at').first()


def get_project_material_deliveries(
    project_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None
) -> models.QuerySet:
    """
    Get material deliveries for a project
    
    Args:
        project_id: UUID of the project
        start_date: Filter deliveries from this date onwards (optional)
        end_date: Filter deliveries up to this date (optional)
        status: Filter by status (optional)
    
    Returns:
        QuerySet of MaterialDelivery objects
    """
    queryset = MaterialDelivery.objects.filter(
        project_id=project_id
    ).select_related(
        'project',
        'supplier',
        'received_by'
    ).order_by('-delivery_date', '-created_at')
    
    if start_date:
        queryset = queryset.filter(delivery_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(delivery_date__lte=end_date)
    if status:
        queryset = queryset.filter(status=status)
    
    return queryset


def get_material_delivery_by_id(delivery_id: str) -> Optional[MaterialDelivery]:
    """
    Get a specific material delivery by ID
    
    Args:
        delivery_id: UUID of the delivery
    
    Returns:
        MaterialDelivery instance or None
    """
    try:
        return MaterialDelivery.objects.select_related(
            'project',
            'supplier',
            'received_by'
        ).get(id=delivery_id)
    except MaterialDelivery.DoesNotExist:
        return None


def get_recent_deliveries(project_id: str, days: int = 7) -> models.QuerySet:
    """
    Get recent material deliveries for a project
    
    Args:
        project_id: UUID of the project
        days: Number of days to look back (default: 7)
    
    Returns:
        QuerySet of recent MaterialDelivery objects
    """
    cutoff_date = date.today() - timedelta(days=days)
    return get_project_material_deliveries(
        project_id=project_id,
        start_date=cutoff_date
    )


def get_project_site_issues(
    project_id: str,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_to_id: Optional[str] = None
) -> models.QuerySet:
    """
    Get site issues for a project
    
    Args:
        project_id: UUID of the project
        status: Filter by status (optional)
        severity: Filter by severity (optional)
        assigned_to_id: Filter by assigned user (optional)
    
    Returns:
        QuerySet of SiteIssue objects
    """
    queryset = SiteIssue.objects.filter(
        project_id=project_id
    ).select_related(
        'project',
        'reported_by',
        'assigned_to'
    ).order_by('-severity', '-reported_date')
    
    if status:
        queryset = queryset.filter(status=status)
    if severity:
        queryset = queryset.filter(severity=severity)
    if assigned_to_id:
        queryset = queryset.filter(assigned_to_id=assigned_to_id)
    
    return queryset


def get_site_issue_by_id(issue_id: str) -> Optional[SiteIssue]:
    """
    Get a specific site issue by ID
    
    Args:
        issue_id: UUID of the issue
    
    Returns:
        SiteIssue instance or None
    """
    try:
        return SiteIssue.objects.select_related(
            'project',
            'reported_by',
            'assigned_to'
        ).get(id=issue_id)
    except SiteIssue.DoesNotExist:
        return None


def get_open_site_issues(project_id: str) -> models.QuerySet:
    """
    Get all open site issues for a project
    
    Args:
        project_id: UUID of the project
    
    Returns:
        QuerySet of open SiteIssue objects
    """
    return get_project_site_issues(project_id).filter(
        status__in=['OPEN', 'IN_PROGRESS']
    )


def get_high_priority_issues(project_id: str) -> models.QuerySet:
    """
    Get high priority (HIGH, CRITICAL) open issues for a project
    
    Args:
        project_id: UUID of the project
    
    Returns:
        QuerySet of high priority SiteIssue objects
    """
    return get_open_site_issues(project_id).filter(
        severity__in=['HIGH', 'CRITICAL']
    )


def get_site_operations_summary(project_id: str) -> Dict[str, Any]:
    """
    Get comprehensive site operations summary for a project
    
    Args:
        project_id: UUID of the project
    
    Returns:
        Dictionary containing summary statistics
    """
    # Get counts
    total_reports = DailySiteReport.objects.filter(project_id=project_id).count()
    total_deliveries = MaterialDelivery.objects.filter(project_id=project_id).count()
    total_issues = SiteIssue.objects.filter(project_id=project_id).count()
    
    # Get open issues stats
    open_issues = get_open_site_issues(project_id)
    open_issues_count = open_issues.count()
    high_priority_count = open_issues.filter(severity__in=['HIGH', 'CRITICAL']).count()
    
    # Get issue breakdown by severity
    issues_by_severity = SiteIssue.objects.filter(
        project_id=project_id,
        status__in=['OPEN', 'IN_PROGRESS']
    ).values('severity').annotate(count=Count('id'))
    
    severity_counts = {
        'CRITICAL': 0,
        'HIGH': 0,
        'MEDIUM': 0,
        'LOW': 0
    }
    for item in issues_by_severity:
        severity_counts[item['severity']] = item['count']
    
    # Get pending deliveries
    pending_deliveries = MaterialDelivery.objects.filter(
        project_id=project_id,
        status='PENDING'
    ).count()
    
    # Get latest activity
    latest_report = get_latest_site_report(project_id)
    latest_delivery = MaterialDelivery.objects.filter(
        project_id=project_id
    ).order_by('-delivery_date').first()
    
    latest_issue = SiteIssue.objects.filter(
        project_id=project_id
    ).order_by('-reported_date').first()
    
    # Get recent reports (last 7 days)
    seven_days_ago = date.today() - timedelta(days=7)
    recent_reports_count = DailySiteReport.objects.filter(
        project_id=project_id,
        report_date__gte=seven_days_ago
    ).count()
    
    return {
        'total_reports': total_reports,
        'recent_reports_count': recent_reports_count,
        'total_deliveries': total_deliveries,
        'pending_deliveries': pending_deliveries,
        'total_issues': total_issues,
        'open_issues_count': open_issues_count,
        'high_priority_issues': high_priority_count,
        'issues_by_severity': severity_counts,
        'latest_report': latest_report,
        'latest_delivery': latest_delivery,
        'latest_issue': latest_issue,
    }


def get_daily_reports_with_issues(project_id: str) -> models.QuerySet:
    """
    Get all daily reports that have issues noted
    
    Args:
        project_id: UUID of the project
    
    Returns:
        QuerySet of DailySiteReport objects with issues
    """
    return DailySiteReport.objects.filter(
        project_id=project_id
    ).exclude(
        Q(issues='') | Q(issues__isnull=True)
    ).select_related(
        'project',
        'prepared_by'
    ).order_by('-report_date')


def get_material_deliveries_by_material(
    project_id: str,
    material_name: str
) -> models.QuerySet:
    """
    Get all deliveries of a specific material
    
    Args:
        project_id: UUID of the project
        material_name: Name of the material
    
    Returns:
        QuerySet of MaterialDelivery objects
    """
    return MaterialDelivery.objects.filter(
        project_id=project_id,
        material_name__icontains=material_name
    ).select_related(
        'project',
        'supplier',
        'received_by'
    ).order_by('-delivery_date')


def get_user_assigned_issues(
    user_id: str,
    project_id: Optional[str] = None
) -> models.QuerySet:
    """
    Get all issues assigned to a specific user
    
    Args:
        user_id: UUID of the user
        project_id: Filter by project (optional)
    
    Returns:
        QuerySet of SiteIssue objects
    """
    queryset = SiteIssue.objects.filter(
        assigned_to_id=user_id
    ).select_related(
        'project',
        'reported_by',
        'assigned_to'
    ).order_by('-severity', '-reported_date')
    
    if project_id:
        queryset = queryset.filter(project_id=project_id)
    
    return queryset
