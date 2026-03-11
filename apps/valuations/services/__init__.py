"""
Valuation Services
Business logic for valuation calculations and operations
Keeps views thin by handling complex calculations here
"""
from decimal import Decimal
from typing import Dict, Any, List, Optional
from django.db import transaction
from django.utils import timezone
from datetime import date

from apps.valuations.models import Valuation, BQItemProgress
from apps.valuations.selectors import (
    get_next_valuation_number,
    get_previous_bq_progress,
    get_project_valuations
)
from apps.projects.models import Project
from apps.bq.models import BQItem


class ValuationService:
    """Service class for valuation operations"""
    
    @staticmethod
    def calculate_valuation_amounts(
        work_completed_value: Decimal,
        retention_percentage: Decimal,
        previous_payments: Decimal
    ) -> Dict[str, Decimal]:
        """
        Calculate retention and amount due
        
        Args:
            work_completed_value: Total value of work completed
            retention_percentage: Retention % to hold back
            previous_payments: Sum of all previous payments
            
        Returns:
            Dictionary with retention_amount and amount_due
        """
        # Calculate retention amount
        retention_amount = (work_completed_value * retention_percentage) / Decimal('100.00')
        
        # Calculate gross amount this period
        gross_this_period = work_completed_value - previous_payments
        
        # Calculate amount due (after retention)
        amount_due = gross_this_period - retention_amount
        
        # Ensure non-negative
        amount_due = max(amount_due, Decimal('0.00'))
        
        return {
            'retention_amount': round(retention_amount, 2),
            'amount_due': round(amount_due, 2)
        }
    
    @staticmethod
    def calculate_work_completed_value(progress_items: List[Dict[str, Any]]) -> Decimal:
        """
        Calculate total work completed value from progress items
        
        Args:
            progress_items: List of dicts with 'bq_item_id', 'this_quantity', etc.
            
        Returns:
            Total cumulative value of work completed
        """
        total = Decimal('0.00')
        
        for item in progress_items:
            bq_item = BQItem.objects.get(id=item['bq_item_id'])
            cumulative_qty = item.get('previous_quantity', 0) + item.get('this_quantity', 0)
            cumulative_value = cumulative_qty * bq_item.rate
            total += cumulative_value
        
        return round(total, 2)
    
    @staticmethod
    @transaction.atomic
    def create_valuation(
        project_id: str,
        valuation_date: date,
        progress_items: List[Dict[str, Any]],
        retention_percentage: Optional[Decimal] = None,
        notes: str = "",
        submitted_by_id: Optional[str] = None
    ) -> Valuation:
        """
        Create a new valuation with progress items
        
        Args:
            project_id: Project UUID
            valuation_date: Date of valuation
            progress_items: List of dicts with BQ item progress
            retention_percentage: Optional override (default 10%)
            notes: Optional notes
            submitted_by_id: User ID who created it
            
        Returns:
            Created Valuation object
            
        Example progress_items:
            [
                {
                    'bq_item_id': 'uuid-here',
                    'this_quantity': Decimal('10.50'),
                    'notes': 'Work completed on ground floor'
                },
                ...
            ]
        """
        project = Project.objects.get(id=project_id)
        
        # Generate valuation number
        valuation_number = get_next_valuation_number(project_id)
        
        # Get previous progress for all items
        previous_progress = get_previous_bq_progress(project_id)
        
        # Calculate total previous payments
        previous_valuations = get_project_valuations(project_id).filter(
            status__in=['APPROVED', 'PAID']
        )
        previous_payments = sum(
            v.amount_due for v in previous_valuations
        ) if previous_valuations.exists() else Decimal('0.00')
        
        # Set default retention if not provided
        if retention_percentage is None:
            retention_percentage = Decimal('10.00')
        
        # Create valuation (initially with zero values)
        valuation = Valuation.objects.create(
            project=project,
            valuation_number=valuation_number,
            valuation_date=valuation_date,
            retention_percentage=retention_percentage,
            previous_payments=previous_payments,
            status=Valuation.Status.DRAFT,
            notes=notes,
            submitted_by_id=submitted_by_id
        )
        
        # Create progress items and calculate total work value
        total_work_value = Decimal('0.00')
        
        for item_data in progress_items:
            bq_item = BQItem.objects.get(id=item_data['bq_item_id'])
            this_quantity = Decimal(str(item_data.get('this_quantity', 0)))
            
            # Get previous quantity for this item
            previous_quantity = previous_progress.get(
                str(bq_item.id),
                Decimal('0.00')
            )
            
            # Calculate cumulative
            cumulative_quantity = previous_quantity + this_quantity
            
            # Calculate values
            previous_value = previous_quantity * bq_item.rate
            this_value = this_quantity * bq_item.rate
            cumulative_value = cumulative_quantity * bq_item.rate
            
            # Create progress record
            BQItemProgress.objects.create(
                valuation=valuation,
                bq_item=bq_item,
                previous_quantity=previous_quantity,
                this_quantity=this_quantity,
                cumulative_quantity=cumulative_quantity,
                previous_value=previous_value,
                this_value=this_value,
                cumulative_value=cumulative_value,
                notes=item_data.get('notes', '')
            )
            
            total_work_value += cumulative_value
        
        # Calculate financial amounts
        amounts = ValuationService.calculate_valuation_amounts(
            total_work_value,
            retention_percentage,
            previous_payments
        )
        
        # Update valuation with calculated amounts
        valuation.work_completed_value = total_work_value
        valuation.retention_amount = amounts['retention_amount']
        valuation.amount_due = amounts['amount_due']
        valuation.save()
        
        return valuation
    
    @staticmethod
    @transaction.atomic
    def update_valuation(
        valuation_id: str,
        progress_items: Optional[List[Dict[str, Any]]] = None,
        retention_percentage: Optional[Decimal] = None,
        notes: Optional[str] = None,
        status: Optional[str] = None
    ) -> Valuation:
        """
        Update an existing valuation
        
        Args:
            valuation_id: Valuation UUID
            progress_items: Optional updated progress items
            retention_percentage: Optional new retention %
            notes: Optional updated notes
            status: Optional new status
            
        Returns:
            Updated Valuation object
        """
        valuation = Valuation.objects.get(id=valuation_id)
        
        # Only allow updates if in DRAFT status
        if valuation.status not in ['DRAFT', 'REJECTED']:
            raise ValueError(f"Cannot update valuation with status {valuation.status}")
        
        # Update retention percentage if provided
        if retention_percentage is not None:
            valuation.retention_percentage = retention_percentage
        
        # Update notes if provided
        if notes is not None:
            valuation.notes = notes
        
        # Update progress items if provided
        if progress_items is not None:
            # Delete existing progress items
            valuation.item_progress.all().delete()
            
            # Get previous progress (excluding this valuation)
            previous_progress = get_previous_bq_progress(
                str(valuation.project_id),
                str(valuation_id)
            )
            
            # Recreate progress items
            total_work_value = Decimal('0.00')
            
            for item_data in progress_items:
                bq_item = BQItem.objects.get(id=item_data['bq_item_id'])
                this_quantity = Decimal(str(item_data.get('this_quantity', 0)))
                
                previous_quantity = previous_progress.get(
                    str(bq_item.id),
                    Decimal('0.00')
                )
                
                cumulative_quantity = previous_quantity + this_quantity
                
                previous_value = previous_quantity * bq_item.rate
                this_value = this_quantity * bq_item.rate
                cumulative_value = cumulative_quantity * bq_item.rate
                
                BQItemProgress.objects.create(
                    valuation=valuation,
                    bq_item=bq_item,
                    previous_quantity=previous_quantity,
                    this_quantity=this_quantity,
                    cumulative_quantity=cumulative_quantity,
                    previous_value=previous_value,
                    this_value=this_value,
                    cumulative_value=cumulative_value,
                    notes=item_data.get('notes', '')
                )
                
                total_work_value += cumulative_value
            
            # Recalculate amounts
            amounts = ValuationService.calculate_valuation_amounts(
                total_work_value,
                valuation.retention_percentage,
                valuation.previous_payments
            )
            
            valuation.work_completed_value = total_work_value
            valuation.retention_amount = amounts['retention_amount']
            valuation.amount_due = amounts['amount_due']
        
        # Update status if provided
        if status is not None:
            valuation.status = status
        
        valuation.save()
        return valuation
    
    @staticmethod
    @transaction.atomic
    def approve_valuation(
        valuation_id: str,
        approved_by_id: str
    ) -> Valuation:
        """
        Approve a valuation
        
        Args:
            valuation_id: Valuation UUID
            approved_by_id: User ID approving
            
        Returns:
            Approved Valuation object
        """
        valuation = Valuation.objects.get(id=valuation_id)
        
        if valuation.status not in ['DRAFT', 'SUBMITTED']:
            raise ValueError(f"Cannot approve valuation with status {valuation.status}")
        
        valuation.status = Valuation.Status.APPROVED
        valuation.approved_by_id = approved_by_id
        valuation.approved_date = timezone.now()
        valuation.save()
        
        return valuation
    
    @staticmethod
    @transaction.atomic
    def mark_as_paid(
        valuation_id: str,
        payment_date: date
    ) -> Valuation:
        """
        Mark a valuation as paid
        
        Args:
            valuation_id: Valuation UUID
            payment_date: Date payment was made
            
        Returns:
            Updated Valuation object
        """
        valuation = Valuation.objects.get(id=valuation_id)
        
        if valuation.status != 'APPROVED':
            raise ValueError(f"Cannot mark as paid: valuation status is {valuation.status}")
        
        valuation.status = Valuation.Status.PAID
        valuation.payment_date = payment_date
        valuation.save()
        
        return valuation
    
    @staticmethod
    @transaction.atomic
    def reject_valuation(
        valuation_id: str,
        notes: str
    ) -> Valuation:
        """
        Reject a valuation
        
        Args:
            valuation_id: Valuation UUID
            notes: Rejection reason
            
        Returns:
            Rejected Valuation object
        """
        valuation = Valuation.objects.get(id=valuation_id)
        
        if valuation.status not in ['DRAFT', 'SUBMITTED']:
            raise ValueError(f"Cannot reject valuation with status {valuation.status}")
        
        valuation.status = Valuation.Status.REJECTED
        valuation.notes = f"{valuation.notes}\n\nREJECTED: {notes}" if valuation.notes else f"REJECTED: {notes}"
        valuation.save()
        
        return valuation
    
    @staticmethod
    def get_valuation_report_data(valuation_id: str) -> Dict[str, Any]:
        """
        Get all data needed for generating a valuation report
        
        Args:
            valuation_id: Valuation UUID
            
        Returns:
            Dictionary with all report data
        """
        from .selectors import get_valuation_by_id, get_valuation_items_grouped
        
        valuation = get_valuation_by_id(valuation_id)
        if not valuation:
            raise ValueError(f"Valuation {valuation_id} not found")
        
        items_grouped = get_valuation_items_grouped(valuation_id)
        
        return {
            'valuation': valuation,
            'project': valuation.project,
            'items_grouped': items_grouped,
            'summary': {
                'work_completed_value': valuation.work_completed_value,
                'retention_percentage': valuation.retention_percentage,
                'retention_amount': valuation.retention_amount,
                'previous_payments': valuation.previous_payments,
                'gross_amount': valuation.gross_amount,
                'amount_due': valuation.amount_due
            }
        }
