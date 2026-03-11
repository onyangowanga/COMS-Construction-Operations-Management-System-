"""
Site Operations Service Layer

Business logic for site operations management including:
- Daily site reports
- Material deliveries
- Site issue tracking
"""

from typing import Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.site_operations.models import (
    DailySiteReport,
    MaterialDelivery,
    SiteIssue
)

User = get_user_model()


class SiteOperationsService:
    """Service class for site operations business logic"""
    
    @staticmethod
    @transaction.atomic
    def create_site_report(
        project_id: str,
        report_date: date,
        weather: str,
        labour_summary: str,
        work_completed: str,
        prepared_by_id: str,
        materials_delivered: str = "",
        issues: str = ""
    ) -> DailySiteReport:
        """
        Create a new daily site report
        
        Args:
            project_id: UUID of the project
            report_date: Date of the report
            weather: Weather condition (SUNNY, CLOUDY, RAINY, STORMY)
            labour_summary: Summary of labour on site
            work_completed: Description of work completed
            prepared_by_id: User ID who prepared the report
            materials_delivered: Materials delivered today (optional)
            issues: Issues or concerns noted (optional)
        
        Returns:
            DailySiteReport instance
        
        Raises:
            ValueError: If report for this date already exists
        """
        # Check if report already exists for this date
        if DailySiteReport.objects.filter(
            project_id=project_id,
            report_date=report_date
        ).exists():
            raise ValueError(
                f"A site report already exists for {report_date}. "
                f"Use update_site_report instead."
            )
        
        report = DailySiteReport.objects.create(
            project_id=project_id,
            report_date=report_date,
            weather=weather,
            labour_summary=labour_summary,
            work_completed=work_completed,
            materials_delivered=materials_delivered,
            issues=issues,
            prepared_by_id=prepared_by_id
        )
        
        return report
    
    @staticmethod
    @transaction.atomic
    def update_site_report(
        report_id: str,
        weather: Optional[str] = None,
        labour_summary: Optional[str] = None,
        work_completed: Optional[str] = None,
        materials_delivered: Optional[str] = None,
        issues: Optional[str] = None
    ) -> DailySiteReport:
        """
        Update an existing site report
        
        Args:
            report_id: UUID of the report to update
            weather: Weather condition (optional)
            labour_summary: Labour summary (optional)
            work_completed: Work completed description (optional)
            materials_delivered: Materials delivered (optional)
            issues: Issues noted (optional)
        
        Returns:
            Updated DailySiteReport instance
        """
        report = DailySiteReport.objects.get(id=report_id)
        
        if weather is not None:
            report.weather = weather
        if labour_summary is not None:
            report.labour_summary = labour_summary
        if work_completed is not None:
            report.work_completed = work_completed
        if materials_delivered is not None:
            report.materials_delivered = materials_delivered
        if issues is not None:
            report.issues = issues
        
        report.save()
        return report
    
    @staticmethod
    @transaction.atomic
    def create_material_delivery(
        project_id: str,
        material_name: str,
        quantity: Decimal,
        delivery_note_number: str,
        delivery_date: date,
        received_by_id: str,
        unit: str = "units",
        supplier_id: Optional[str] = None,
        supplier_name: Optional[str] = None,
        status: str = "PENDING",
        notes: str = ""
    ) -> MaterialDelivery:
        """
        Record a new material delivery
        
        Args:
            project_id: UUID of the project
            material_name: Name of the material
            quantity: Quantity delivered
            delivery_note_number: Delivery note reference number
            delivery_date: Date of delivery
            received_by_id: User ID who received the delivery
            unit: Unit of measurement (default: "units")
            supplier_id: Supplier UUID (optional)
            supplier_name: Supplier name if not in system (optional)
            status: Delivery status (PENDING, ACCEPTED, REJECTED, PARTIAL)
            notes: Additional notes (optional)
        
        Returns:
            MaterialDelivery instance
        """
        delivery = MaterialDelivery.objects.create(
            project_id=project_id,
            material_name=material_name,
            quantity=quantity,
            unit=unit,
            delivery_note_number=delivery_note_number,
            delivery_date=delivery_date,
            received_by_id=received_by_id,
            supplier_id=supplier_id,
            supplier_name=supplier_name or "",
            status=status,
            notes=notes
        )
        
        return delivery
    
    @staticmethod
    @transaction.atomic
    def update_delivery_status(
        delivery_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> MaterialDelivery:
        """
        Update the status of a material delivery
        
        Args:
            delivery_id: UUID of the delivery
            status: New status (PENDING, ACCEPTED, REJECTED, PARTIAL)
            notes: Additional notes about the status change (optional)
        
        Returns:
            Updated MaterialDelivery instance
        """
        delivery = MaterialDelivery.objects.get(id=delivery_id)
        delivery.status = status
        
        if notes is not None:
            if delivery.notes:
                delivery.notes += f"\n\n[{timezone.now()}] {notes}"
            else:
                delivery.notes = notes
        
        delivery.save()
        return delivery
    
    @staticmethod
    @transaction.atomic
    def create_site_issue(
        project_id: str,
        title: str,
        description: str,
        severity: str,
        reported_by_id: str,
        assigned_to_id: Optional[str] = None,
        status: str = "OPEN"
    ) -> SiteIssue:
        """
        Create a new site issue
        
        Args:
            project_id: UUID of the project
            title: Brief title of the issue
            description: Detailed description
            severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
            reported_by_id: User ID who reported the issue
            assigned_to_id: User ID to assign the issue to (optional)
            status: Initial status (default: OPEN)
        
        Returns:
            SiteIssue instance
        """
        issue = SiteIssue.objects.create(
            project_id=project_id,
            title=title,
            description=description,
            severity=severity,
            status=status,
            reported_by_id=reported_by_id,
            assigned_to_id=assigned_to_id
        )
        
        return issue
    
    @staticmethod
    @transaction.atomic
    def update_site_issue(
        issue_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        assigned_to_id: Optional[str] = None
    ) -> SiteIssue:
        """
        Update an existing site issue
        
        Args:
            issue_id: UUID of the issue
            title: New title (optional)
            description: New description (optional)
            severity: New severity (optional)
            status: New status (optional)
            assigned_to_id: User ID to reassign to (optional)
        
        Returns:
            Updated SiteIssue instance
        """
        issue = SiteIssue.objects.get(id=issue_id)
        
        if title is not None:
            issue.title = title
        if description is not None:
            issue.description = description
        if severity is not None:
            issue.severity = severity
        if status is not None:
            # Auto-set resolved_date when status changes to RESOLVED
            if status == 'RESOLVED' and issue.status != 'RESOLVED':
                issue.resolved_date = timezone.now()
            issue.status = status
        if assigned_to_id is not None:
            issue.assigned_to_id = assigned_to_id
        
        issue.save()
        return issue
    
    @staticmethod
    @transaction.atomic
    def resolve_site_issue(
        issue_id: str,
        resolution_notes: str
    ) -> SiteIssue:
        """
        Mark a site issue as resolved
        
        Args:
            issue_id: UUID of the issue
            resolution_notes: Notes explaining how the issue was resolved
        
        Returns:
            Updated SiteIssue instance
        """
        issue = SiteIssue.objects.get(id=issue_id)
        issue.status = 'RESOLVED'
        issue.resolved_date = timezone.now()
        issue.resolution_notes = resolution_notes
        issue.save()
        
        return issue
    
    @staticmethod
    @transaction.atomic
    def reopen_site_issue(
        issue_id: str,
        reason: str
    ) -> SiteIssue:
        """
        Reopen a resolved issue
        
        Args:
            issue_id: UUID of the issue
            reason: Reason for reopening
        
        Returns:
            Updated SiteIssue instance
        """
        issue = SiteIssue.objects.get(id=issue_id)
        issue.status = 'OPEN'
        issue.resolved_date = None
        
        # Append reason to resolution notes
        if issue.resolution_notes:
            issue.resolution_notes += f"\n\n[REOPENED {timezone.now()}] {reason}"
        else:
            issue.resolution_notes = f"[REOPENED {timezone.now()}] {reason}"
        
        issue.save()
        return issue
