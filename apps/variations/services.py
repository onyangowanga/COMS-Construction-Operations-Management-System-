"""
Variation Order Service Layer

Business logic for variation order management, approval workflow,
and financial impact calculations.
"""

from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.variations.models import VariationOrder
from apps.projects.models import Project
from apps.authentication.models import User


class VariationService:
    """Service for managing variation orders and their lifecycle"""
    
    @staticmethod
    def generate_reference_number(project: Project) -> str:
        """
        Generate unique variation order reference number.
        
        Format: VO-{PROJECT_CODE}-{YEAR}-{SEQUENCE}
        Example: VO-PRJ001-2026-001
        """
        from datetime import datetime
        
        year = datetime.now().year
        project_code = project.project_code or str(project.id)[:6]
        
        # Get last variation for this project in current year
        last_variation = VariationOrder.objects.filter(
            project=project,
            instruction_date__year=year
        ).order_by('-reference_number').first()
        
        if last_variation and last_variation.reference_number:
            # Extract sequence number
            parts = last_variation.reference_number.split('-')
            if len(parts) >= 4:
                try:
                    last_seq = int(parts[-1])
                    sequence = last_seq + 1
                except (ValueError, IndexError):
                    sequence = 1
            else:
                sequence = 1
        else:
            sequence = 1
        
        return f"VO-{project_code}-{year}-{sequence:03d}"
    
    @staticmethod
    @transaction.atomic
    def create_variation(
        project_id: str,
        title: str,
        description: str,
        estimated_value: Decimal,
        instruction_date: Any,
        created_by: User,
        change_type: str = 'SCOPE_CHANGE',
        priority: str = 'MEDIUM',
        **kwargs
    ) -> VariationOrder:
        """
        Create a new variation order.
        
        Args:
            project_id: Project UUID
            title: Variation title
            description: Detailed description
            estimated_value: Estimated cost
            instruction_date: Date of instruction
            created_by: User creating the variation
            change_type: Type of change (default: SCOPE_CHANGE)
            priority: Priority level (default: MEDIUM)
            **kwargs: Additional fields
        
        Returns:
            VariationOrder instance
        """
        project = Project.objects.select_for_update().get(id=project_id)
        
        # Generate reference number
        reference_number = VariationService.generate_reference_number(project)
        
        # Create variation order
        variation = VariationOrder.objects.create(
            project=project,
            reference_number=reference_number,
            title=title,
            description=description,
            estimated_value=estimated_value,
            instruction_date=instruction_date,
            created_by=created_by,
            change_type=change_type,
            priority=priority,
            status=VariationOrder.Status.DRAFT,
            **kwargs
        )
        
        return variation
    
    @staticmethod
    @transaction.atomic
    def submit_for_approval(
        variation_id: str,
        submitted_by: User
    ) -> VariationOrder:
        """
        Submit variation for approval.
        
        Args:
            variation_id: Variation UUID
            submitted_by: User submitting the variation
        
        Returns:
            Updated VariationOrder
        
        Raises:
            ValidationError: If variation cannot be submitted
        """
        variation = VariationOrder.objects.select_for_update().get(id=variation_id)
        
        if not variation.can_submit():
            raise ValidationError(
                f"Variation {variation.reference_number} cannot be submitted. "
                f"Current status: {variation.get_status_display()}"
            )
        
        # Update status
        variation.status = VariationOrder.Status.SUBMITTED
        variation.submitted_by = submitted_by
        variation.submitted_date = timezone.now()
        variation.save()
        
        return variation
    
    @staticmethod
    @transaction.atomic
    def approve_variation(
        variation_id: str,
        approved_by: User,
        approved_value: Optional[Decimal] = None,
        notes: str = ''
    ) -> VariationOrder:
        """
        Approve a variation order and update project financials.
        
        This is the critical method that triggers financial impact:
        1. Approve the variation
        2. Update project contract_sum
        3. Trigger portfolio metrics recalculation
        4. Update cash flow forecasts
        
        Args:
            variation_id: Variation UUID
            approved_by: User approving the variation
            approved_value: Approved amount (defaults to estimated_value)
            notes: Approval notes
        
        Returns:
            Updated VariationOrder
        
        Raises:
            ValidationError: If variation cannot be approved
        """
        variation = VariationOrder.objects.select_for_update().get(id=variation_id)
        
        if not variation.can_approve():
            raise ValidationError(
                f"Variation {variation.reference_number} cannot be approved. "
                f"Current status: {variation.get_status_display()}"
            )
        
        # Set approved value (default to estimated if not specified)
        if approved_value is None:
            approved_value = variation.estimated_value
        
        # Update variation
        variation.status = VariationOrder.Status.APPROVED
        variation.approved_by = approved_by
        variation.approved_date = timezone.now()
        variation.approved_value = approved_value
        
        if notes:
            variation.technical_notes = (
                f"{variation.technical_notes}\n\nApproval Notes: {notes}"
                if variation.technical_notes
                else f"Approval Notes: {notes}"
            )
        
        variation.save()
        
        # === FINANCIAL IMPACT ===
        
        # 1. Update project contract sum
        VariationService._update_project_contract_value(
            variation.project,
            approved_value
        )
        
        # 2. Update portfolio metrics
        VariationService._update_portfolio_metrics(variation.project)
        
        # 3. Update cash flow forecasts
        VariationService._update_cash_flow_forecasts(variation.project)
        
        return variation
    
    @staticmethod
    @transaction.atomic
    def reject_variation(
        variation_id: str,
        rejected_by: User,
        rejection_reason: str
    ) -> VariationOrder:
        """
        Reject a variation order.
        
        Args:
            variation_id: Variation UUID
            rejected_by: User rejecting the variation
            rejection_reason: Reason for rejection
        
        Returns:
            Updated VariationOrder
        
        Raises:
            ValidationError: If variation cannot be rejected
        """
        variation = VariationOrder.objects.select_for_update().get(id=variation_id)
        
        if not variation.can_reject():
            raise ValidationError(
                f"Variation {variation.reference_number} cannot be rejected. "
                f"Current status: {variation.get_status_display()}"
            )
        
        variation.status = VariationOrder.Status.REJECTED
        variation.rejection_reason = rejection_reason
        variation.save()
        
        return variation
    
    @staticmethod
    @transaction.atomic
    def certify_variation(
        variation_id: str,
        certified_by: User,
        certified_amount: Decimal,
        notes: str = ''
    ) -> VariationOrder:
        """
        Certify a variation order by consultant (QS, Architect, Engineer).
        
        Consultant certification may occur before or after approval.
        Certified amount may differ from approved value.
        
        Args:
            variation_id: Variation UUID
            certified_by: Consultant certifying the variation
            certified_amount: Amount certified by consultant
            notes: Optional certification notes
        
        Returns:
            Updated VariationOrder
        
        Raises:
            ValidationError: If variation cannot be certified
        """
        variation = VariationOrder.objects.select_for_update().get(id=variation_id)
        
        if not variation.can_certify():
            raise ValidationError(
                f"Variation {variation.reference_number} cannot be certified. "
                f"Current status: {variation.get_status_display()}"
            )
        
        variation.certified_by = certified_by
        variation.certified_amount = certified_amount
        variation.certified_date = timezone.now()
        variation.save()
        
        return variation
    
    @staticmethod
    @transaction.atomic
    def mark_as_invoiced(
        variation_id: str,
        invoiced_value: Decimal
    ) -> VariationOrder:
        """
        Mark variation as invoiced.
        
        Args:
            variation_id: Variation UUID
            invoiced_value: Amount invoiced
        
        Returns:
            Updated VariationOrder
        """
        variation = VariationOrder.objects.select_for_update().get(id=variation_id)
        
        if not variation.can_invoice():
            raise ValidationError(
                f"Variation {variation.reference_number} cannot be invoiced. "
                f"Current status: {variation.get_status_display()}"
            )
        
        variation.status = VariationOrder.Status.INVOICED
        variation.invoiced_value = invoiced_value
        variation.save()
        
        return variation
    
    @staticmethod
    @transaction.atomic
    def mark_as_paid(
        variation_id: str,
        paid_value: Decimal
    ) -> VariationOrder:
        """
        Mark variation as paid.
        
        Args:
            variation_id: Variation UUID
            paid_value: Amount paid
        
        Returns:
            Updated VariationOrder
        """
        variation = VariationOrder.objects.select_for_update().get(id=variation_id)
        
        if variation.status != VariationOrder.Status.INVOICED:
            raise ValidationError(
                f"Variation must be invoiced before marking as paid. "
                f"Current status: {variation.get_status_display()}"
            )
        
        variation.status = VariationOrder.Status.PAID
        variation.paid_value = paid_value
        variation.save()
        
        return variation
    
    # === PRIVATE HELPER METHODS ===
    
    @staticmethod
    def _update_project_contract_value(project: Project, variation_value: Decimal):
        """
        Update project contract sum when variation is approved.
        
        Args:
            project: Project instance
            variation_value: Approved variation value to add
        """
        if project.contract_sum:
            project.contract_sum += variation_value
        else:
            project.contract_sum = variation_value
        
        project.save(update_fields=['contract_sum'])
    
    @staticmethod
    def _update_portfolio_metrics(project: Project):
        """
        Trigger portfolio metrics recalculation.
        
        Args:
            project: Project instance
        """
        try:
            from apps.portfolio.services import PortfolioService
            
            # Recalculate project metrics
            PortfolioService.calculate_project_metrics(str(project.id))
            
        except (ImportError, Exception) as e:
            # Portfolio module may not be available
            print(f"Could not update portfolio metrics: {e}")
    
    @staticmethod
    def _update_cash_flow_forecasts(project: Project):
        """
        Update cash flow forecasts to reflect variation impact.
        
        Args:
            project: Project instance
        """
        try:
            from apps.cashflow.services import CashFlowService
            
            # Regenerate cash flow forecast
            CashFlowService.generate_project_forecast(
                project_id=str(project.id),
                horizon_months=6
            )
            
        except (ImportError, Exception) as e:
            # Cash flow module may not be available
            print(f"Could not update cash flow forecasts: {e}")
    
    @staticmethod
    def get_project_variation_summary(project_id: str) -> Dict[str, Any]:
        """
        Get variation order summary for a project.
        
        Args:
            project_id: Project UUID
        
        Returns:
            Dictionary with summary metrics
        """
        from django.db.models import Sum, Count, Q
        
        variations = VariationOrder.objects.filter(project_id=project_id)
        
        summary = variations.aggregate(
            total_count=Count('id'),
            pending_count=Count('id', filter=Q(status=VariationOrder.Status.SUBMITTED)),
            approved_count=Count('id', filter=Q(status=VariationOrder.Status.APPROVED)),
            rejected_count=Count('id', filter=Q(status=VariationOrder.Status.REJECTED)),
            total_estimated=Sum('estimated_value'),
            total_approved=Sum('approved_value', filter=Q(status__in=[
                VariationOrder.Status.APPROVED,
                VariationOrder.Status.INVOICED,
                VariationOrder.Status.PAID
            ])),
            total_invoiced=Sum('invoiced_value'),
            total_paid=Sum('paid_value'),
        )
        
        return {
            'total_variations': summary['total_count'] or 0,
            'pending_variations': summary['pending_count'] or 0,
            'approved_variations': summary['approved_count'] or 0,
            'rejected_variations': summary['rejected_count'] or 0,
            'total_estimated_value': summary['total_estimated'] or Decimal('0.00'),
            'total_approved_value': summary['total_approved'] or Decimal('0.00'),
            'total_invoiced_value': summary['total_invoiced'] or Decimal('0.00'),
            'total_paid_value': summary['total_paid'] or Decimal('0.00'),
            'outstanding_value': (summary['total_approved'] or Decimal('0.00')) - (summary['total_paid'] or Decimal('0.00')),
        }
