"""
Subcontractor Management - Service Layer

Business logic for subcontract operations including:
- Subcontract creation and management
- Claim submission workflow
- Claim certification workflow
- Payment tracking
- Financial integration

All operations are transaction-safe and include proper validation.
"""

from decimal import Decimal
from typing import Optional
from datetime import date

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.subcontracts.models import (
    Subcontractor,
    SubcontractAgreement,
    SubcontractClaim
)
from apps.authentication.models import User
from apps.projects.models import Project


class SubcontractService:
    """
    Service layer for subcontract operations.
    
    All operations are transaction-safe and include proper validation.
    """
    
    @staticmethod
    @transaction.atomic
    def create_subcontractor(
        organization,
        name: str,
        contact_person: str,
        phone: str,
        email: str,
        address: str,
        created_by: User,
        company_registration: str = '',
        tax_number: str = '',
        specialization: str = '',
        notes: str = ''
    ) -> Subcontractor:
        """
        Create a new subcontractor record.
        
        Args:
            organization: Organization instance
            name: Subcontractor company name
            contact_person: Primary contact person
            phone: Contact phone number
            email: Contact email address
            address: Physical address
            created_by: User creating the record
            company_registration: Company registration number
            tax_number: Tax identification number
            specialization: Area of specialization
            notes: Additional notes
        
        Returns:
            Subcontractor instance
        
        Example:
            subcontractor = SubcontractService.create_subcontractor(
                organization=org,
                name="ABC Electrical Works",
                contact_person="John Doe",
                phone="+254712345678",
                email="john@abcelectrical.com",
                address="123 Industrial Area, Nairobi",
                created_by=user,
                specialization="Electrical Installation"
            )
        """
        subcontractor = Subcontractor.objects.create(
            organization=organization,
            name=name,
            company_registration=company_registration,
            tax_number=tax_number,
            contact_person=contact_person,
            phone=phone,
            email=email,
            address=address,
            specialization=specialization,
            notes=notes,
            created_by=created_by
        )
        
        return subcontractor
    
    @staticmethod
    def generate_contract_reference(project: Project) -> str:
        """Generate subcontract reference in the format SC-{PROJECT_CODE}-{YEAR}-{SEQ}."""
        year = timezone.now().year
        project_code = (getattr(project, 'code', None) or str(project.id)[:6]).upper()
        prefix = f"SC-{project_code}-{year}-"

        last_contract = SubcontractAgreement.objects.select_for_update().filter(
            project=project,
            contract_reference__startswith=prefix,
        ).order_by('-contract_reference').first()

        sequence = 1
        if last_contract and last_contract.contract_reference:
            try:
                sequence = int(last_contract.contract_reference.split('-')[-1]) + 1
            except (ValueError, IndexError):
                sequence = 1

        return f"{prefix}{sequence:03d}"

    @staticmethod
    def generate_claim_number(subcontract: SubcontractAgreement) -> str:
        """Generate subcontract claim number in the format {CONTRACT_REFERENCE}-C{SEQ}."""
        prefix = f"{subcontract.contract_reference}-C"

        last_claim = SubcontractClaim.objects.select_for_update().filter(
            subcontract=subcontract,
            claim_number__startswith=prefix,
        ).order_by('-claim_number').first()

        sequence = 1
        if last_claim and last_claim.claim_number:
            try:
                sequence = int(last_claim.claim_number.split('-C')[-1]) + 1
            except (ValueError, IndexError):
                sequence = 1

        return f"{prefix}{sequence:03d}"

    @staticmethod
    @transaction.atomic
    def create_subcontract(
        project: Project,
        subcontractor: Subcontractor,
        contract_reference: Optional[str],
        scope_of_work: str,
        contract_value: Decimal,
        start_date: date,
        end_date: date,
        created_by: User,
        retention_percentage: Decimal = Decimal('10.00'),
        payment_terms: str = '',
        vat_applicable: bool = True,
        performance_bond_required: bool = False,
        performance_bond_percentage: Optional[Decimal] = None,
        notes: str = ''
    ) -> SubcontractAgreement:
        """
        Create a new subcontract agreement.
        
        Args:
            project: Project instance
            subcontractor: Subcontractor instance
            contract_reference: Unique contract reference (e.g., SC-2026-001)
            scope_of_work: Detailed work description
            contract_value: Total contract value
            start_date: Contract start date
            end_date: Contract end date
            created_by: User creating the agreement
            retention_percentage: Retention % (default 10%)
            payment_terms: Payment terms description
            vat_applicable: Whether VAT applies
            performance_bond_required: Whether bond is required
            performance_bond_percentage: Bond percentage if required
            notes: Additional notes
        
        Returns:
            SubcontractAgreement instance
        
        Raises:
            ValidationError: If validation fails
        
        Example:
            agreement = SubcontractService.create_subcontract(
                project=project,
                subcontractor=subcontractor,
                contract_reference="SC-2026-001",
                scope_of_work="Complete electrical installation",
                contract_value=Decimal('5000000.00'),
                start_date=date(2026, 3, 1),
                end_date=date(2026, 8, 31),
                created_by=user,
                retention_percentage=Decimal('10.00')
            )
        """
        # Validation
        if start_date >= end_date:
            raise ValidationError("End date must be after start date")
        
        if contract_value <= 0:
            raise ValidationError("Contract value must be greater than zero")
        
        if retention_percentage < 0 or retention_percentage > 100:
            raise ValidationError("Retention percentage must be between 0 and 100")
        
        # Check subcontractor belongs to same organization
        if subcontractor.organization != project.organization:
            raise ValidationError("Subcontractor must belong to the same organization")
        
        contract_reference = contract_reference or SubcontractService.generate_contract_reference(project)

        # Create subcontract
        subcontract = SubcontractAgreement.objects.create(
            project=project,
            subcontractor=subcontractor,
            contract_reference=contract_reference,
            scope_of_work=scope_of_work,
            contract_value=contract_value,
            retention_percentage=retention_percentage,
            start_date=start_date,
            end_date=end_date,
            status=SubcontractAgreement.Status.DRAFT,
            payment_terms=payment_terms,
            vat_applicable=vat_applicable,
            performance_bond_required=performance_bond_required,
            performance_bond_percentage=performance_bond_percentage,
            notes=notes,
            created_by=created_by
        )
        
        return subcontract
    
    @staticmethod
    @transaction.atomic
    def activate_subcontract(
        subcontract: SubcontractAgreement,
        activated_by: User
    ) -> SubcontractAgreement:
        """
        Activate a draft subcontract.
        
        Args:
            subcontract: SubcontractAgreement instance
            activated_by: User activating the contract
        
        Returns:
            Updated SubcontractAgreement instance
        
        Raises:
            ValidationError: If contract is not in DRAFT status
        """
        if subcontract.status != SubcontractAgreement.Status.DRAFT:
            raise ValidationError("Only DRAFT contracts can be activated")
        
        subcontract.status = SubcontractAgreement.Status.ACTIVE
        subcontract.activated_at = timezone.now()
        subcontract.save(update_fields=['status', 'activated_at', 'updated_at'])
        
        return subcontract
    
    @staticmethod
    @transaction.atomic
    def submit_claim(
        subcontract: SubcontractAgreement,
        claim_number: Optional[str],
        period_start: date,
        period_end: date,
        claimed_amount: Decimal,
        submitted_by: User,
        description: str = '',
        notes: str = ''
    ) -> SubcontractClaim:
        """
        Submit a new payment claim for a subcontract.
        
        Args:
            subcontract: SubcontractAgreement instance
            claim_number: Unique claim number (e.g., SC-001-C001)
            period_start: Claim period start date
            period_end: Claim period end date
            claimed_amount: Amount being claimed
            submitted_by: User submitting the claim
            description: Work description
            notes: Additional notes
        
        Returns:
            SubcontractClaim instance
        
        Raises:
            ValidationError: If validation fails
        
        Example:
            claim = SubcontractService.submit_claim(
                subcontract=agreement,
                claim_number="SC-001-C001",
                period_start=date(2026, 3, 1),
                period_end=date(2026, 3, 31),
                claimed_amount=Decimal('500000.00'),
                submitted_by=user,
                description="Month 1 - Foundation work completed"
            )
        """
        # Validation
        if subcontract.status != SubcontractAgreement.Status.ACTIVE:
            raise ValidationError("Cannot submit claim for inactive subcontract")
        
        if period_start >= period_end:
            raise ValidationError("Period end must be after period start")
        
        if claimed_amount <= 0:
            raise ValidationError("Claimed amount must be greater than zero")
        
        # Check cumulative amount doesn't exceed contract value
        total_claimed = subcontract.total_claimed + claimed_amount
        if total_claimed > subcontract.contract_value:
            raise ValidationError(
                f"Total claimed amount ({total_claimed}) would exceed "
                f"contract value ({subcontract.contract_value})"
            )
        
        # Calculate previous cumulative
        previous_cumulative = subcontract.total_certified

        claim_number = claim_number or SubcontractService.generate_claim_number(subcontract)
        
        # Create claim
        claim = SubcontractClaim.objects.create(
            subcontract=subcontract,
            claim_number=claim_number,
            period_start=period_start,
            period_end=period_end,
            claimed_amount=claimed_amount,
            previous_cumulative_amount=previous_cumulative,
            status=SubcontractClaim.Status.SUBMITTED,
            description=description,
            notes=notes,
            submitted_by=submitted_by,
            submitted_date=timezone.now(),
            created_by=submitted_by
        )
        
        return claim
    
    @staticmethod
    @transaction.atomic
    def certify_claim(
        claim: SubcontractClaim,
        certified_amount: Decimal,
        certified_by: User,
        notes: str = ''
    ) -> SubcontractClaim:
        """
        Certify a submitted payment claim.
        
        This approves the claim for payment and triggers financial integration:
        - Updates project expenses
        - Updates cash flow forecasts
        - Updates portfolio metrics
        
        Args:
            claim: SubcontractClaim instance
            certified_amount: Amount being certified (may differ from claimed)
            certified_by: User certifying the claim
            notes: Certification notes
        
        Returns:
            Updated SubcontractClaim instance
        
        Raises:
            ValidationError: If validation fails
        
        Example:
            certified_claim = SubcontractService.certify_claim(
                claim=claim,
                certified_amount=Decimal('480000.00'),
                certified_by=project_manager,
                notes="Approved with 4% deduction for incomplete work"
            )
        """
        # Validation
        if claim.status != SubcontractClaim.Status.SUBMITTED:
            raise ValidationError("Only SUBMITTED claims can be certified")
        
        if certified_amount < 0:
            raise ValidationError("Certified amount cannot be negative")
        
        if certified_amount > claim.claimed_amount:
            raise ValidationError("Certified amount cannot exceed claimed amount")
        
        # Calculate retention
        retention_amount = (
            certified_amount * claim.subcontract.retention_percentage
        ) / Decimal('100')
        
        # Update claim
        claim.certified_amount = certified_amount
        claim.retention_amount = retention_amount
        claim.status = SubcontractClaim.Status.CERTIFIED
        claim.certified_by = certified_by
        claim.certified_date = timezone.now()
        if notes:
            claim.notes = notes if not claim.notes else f"{claim.notes}\n\n{notes}"
        claim.save(update_fields=[
            'certified_amount',
            'retention_amount',
            'status',
            'certified_by',
            'certified_date',
            'notes',
            'updated_at'
        ])
        
        # === FINANCIAL INTEGRATION ===
        
        # Update project expenses (if you have a project expenses model)
        # This is where you'd create expense records or update budgets
        
        # Update cash flow forecasts
        # Add expected payment to cash flow
        SubcontractService._update_cashflow_forecast(claim)
        
        # Update portfolio metrics
        # Recalculate EVM metrics if applicable
        SubcontractService._update_portfolio_metrics(claim)
        
        return claim
    
    @staticmethod
    @transaction.atomic
    def reject_claim(
        claim: SubcontractClaim,
        rejection_reason: str,
        rejected_by: User
    ) -> SubcontractClaim:
        """
        Reject a submitted payment claim.
        
        Args:
            claim: SubcontractClaim instance
            rejection_reason: Reason for rejection
            rejected_by: User rejecting the claim
        
        Returns:
            Updated SubcontractClaim instance
        
        Raises:
            ValidationError: If claim is not in SUBMITTED status
        
        Example:
            rejected_claim = SubcontractService.reject_claim(
                claim=claim,
                rejection_reason="Incomplete documentation",
                rejected_by=project_manager
            )
        """
        if claim.status != SubcontractClaim.Status.SUBMITTED:
            raise ValidationError("Only SUBMITTED claims can be rejected")
        
        if not rejection_reason:
            raise ValidationError("Rejection reason is required")
        
        claim.status = SubcontractClaim.Status.REJECTED
        claim.rejection_reason = rejection_reason
        claim.certified_by = rejected_by  # Track who rejected it
        claim.certified_date = timezone.now()
        claim.save(update_fields=[
            'status',
            'rejection_reason',
            'certified_by',
            'certified_date',
            'updated_at'
        ])
        
        return claim
    
    @staticmethod
    @transaction.atomic
    def mark_claim_paid(
        claim: SubcontractClaim,
        paid_by: User,
        payment_reference: str = ''
    ) -> SubcontractClaim:
        """
        Mark a certified claim as paid.
        
        Args:
            claim: SubcontractClaim instance
            paid_by: User marking as paid
            payment_reference: Payment reference number
        
        Returns:
            Updated SubcontractClaim instance
        
        Raises:
            ValidationError: If claim is not CERTIFIED
        
        Example:
            paid_claim = SubcontractService.mark_claim_paid(
                claim=certified_claim,
                paid_by=accounts_manager,
                payment_reference="PAY-2026-12345"
            )
        """
        if claim.status != SubcontractClaim.Status.CERTIFIED:
            raise ValidationError("Only CERTIFIED claims can be marked as paid")
        
        claim.status = SubcontractClaim.Status.PAID
        claim.paid_date = timezone.now()
        if payment_reference:
            claim.notes = (
                f"{claim.notes}\n\nPayment Reference: {payment_reference}"
                if claim.notes else f"Payment Reference: {payment_reference}"
            )
        claim.save(update_fields=['status', 'paid_date', 'notes', 'updated_at'])
        
        # Update cash flow actuals
        SubcontractService._record_payment_in_cashflow(claim)
        
        return claim
    
    @staticmethod
    @transaction.atomic
    def complete_subcontract(
        subcontract: SubcontractAgreement,
        completed_by: User
    ) -> SubcontractAgreement:
        """
        Mark a subcontract as completed.
        
        Args:
            subcontract: SubcontractAgreement instance
            completed_by: User completing the contract
        
        Returns:
            Updated SubcontractAgreement instance
        
        Raises:
            ValidationError: If contract is not ACTIVE
        """
        if subcontract.status != SubcontractAgreement.Status.ACTIVE:
            raise ValidationError("Only ACTIVE contracts can be completed")
        
        # Check for pending claims
        pending_claims = subcontract.claims.filter(
            status__in=[
                SubcontractClaim.Status.DRAFT,
                SubcontractClaim.Status.SUBMITTED,
                SubcontractClaim.Status.CERTIFIED
            ]
        ).count()
        
        if pending_claims > 0:
            raise ValidationError(
                f"Cannot complete contract with {pending_claims} pending claims"
            )
        
        subcontract.status = SubcontractAgreement.Status.COMPLETED
        subcontract.completed_at = timezone.now()
        subcontract.save(update_fields=['status', 'completed_at', 'updated_at'])
        
        return subcontract
    
    # === PRIVATE HELPER METHODS FOR FINANCIAL INTEGRATION ===
    
    @staticmethod
    def _update_cashflow_forecast(claim: SubcontractClaim):
        """
        Update cash flow forecast with expected payment.
        
        Integration with cashflow module.
        """
        try:
            from apps.cashflow.services import CashFlowService
            
            # Calculate net payment (certified - retention)
            net_amount = claim.net_payment_amount
            
            # Add to cash flow forecast as expense
            # This is a placeholder - adjust based on your cashflow module structure
            # CashFlowService.add_forecast_item(
            #     project=claim.subcontract.project,
            #     amount=-net_amount,  # Negative for expense
            #     date=claim.certified_date.date(),
            #     category='SUBCONTRACTOR_PAYMENT',
            #     description=f"Subcontract Payment: {claim.claim_number}"
            # )
        except ImportError:
            # Cashflow module not available
            pass
    
    @staticmethod
    def _update_portfolio_metrics(claim: SubcontractClaim):
        """
        Update portfolio metrics with certified amounts.
        
        Integration with portfolio module for EVM calculations.
        """
        try:
            from apps.portfolio.services import PortfolioService
            
            # Update actual cost (AC) with certified amount
            # This is a placeholder - adjust based on your portfolio module structure
            # PortfolioService.update_actual_cost(
            #     project=claim.subcontract.project,
            #     amount=claim.certified_amount
            # )
        except ImportError:
            # Portfolio module not available
            pass
    
    @staticmethod
    def _record_payment_in_cashflow(claim: SubcontractClaim):
        """
        Record actual payment in cash flow.
        
        Integration with cashflow module for actual expenses.
        """
        try:
            from apps.cashflow.services import CashFlowService
            
            # Record actual payment
            # This is a placeholder - adjust based on your cashflow module structure
            # CashFlowService.record_actual_expense(
            #     project=claim.subcontract.project,
            #     amount=claim.net_payment_amount,
            #     date=claim.paid_date.date(),
            #     category='SUBCONTRACTOR_PAYMENT',
            #     reference=claim.claim_number
            # )
        except ImportError:
            # Cashflow module not available
            pass
