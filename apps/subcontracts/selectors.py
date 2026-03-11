"""
Subcontractor Management - Selector Layer

Optimized database queries for subcontract and claim retrieval.
All selectors use select_related and prefetch_related for efficiency.
"""

from typing import Optional
from decimal import Decimal
from django.db.models import Q, QuerySet, Sum, Count, Avg, Max, Min
from django.db.models.functions import Coalesce

from apps.subcontracts.models import (
    Subcontractor,
    SubcontractAgreement,
    SubcontractClaim
)


class SubcontractorSelector:
    """
    Optimized selectors for subcontractor queries.
    """
    
    @staticmethod
    def get_base_queryset() -> QuerySet:
        """
        Get base queryset with common optimizations.
        
        Returns:
            Optimized QuerySet
        """
        return Subcontractor.objects.select_related(
            'organization',
            'created_by'
        )
    
    @staticmethod
    def get_active_subcontractors(organization) -> QuerySet:
        """
        Get all active subcontractors for an organization.
        
        Args:
            organization: Organization instance
        
        Returns:
            QuerySet of active Subcontractor instances
        """
        return SubcontractorSelector.get_base_queryset().filter(
            organization=organization,
            is_active=True
        ).order_by('name')
    
    @staticmethod
    def get_subcontractor_with_stats(subcontractor_id: str):
        """
        Get subcontractor with contract statistics.
        
        Args:
            subcontractor_id: UUID of subcontractor
        
        Returns:
            Subcontractor instance with annotated stats
        """
        return SubcontractorSelector.get_base_queryset().annotate(
            contracts_count=Count('subcontracts'),
            active_contracts=Count(
                'subcontracts',
                filter=Q(subcontracts__status=SubcontractAgreement.Status.ACTIVE)
            ),
            total_contract_value=Coalesce(
                Sum(
                    'subcontracts__contract_value',
                    filter=Q(subcontracts__status=SubcontractAgreement.Status.ACTIVE)
                ),
                Decimal('0.00')
            )
        ).get(id=subcontractor_id)
    
    @staticmethod
    def search_subcontractors(
        organization,
        query: str,
        active_only: bool = True
    ) -> QuerySet:
        """
        Search subcontractors by name, specialization, or contact.
        
        Args:
            organization: Organization instance
            query: Search query string
            active_only: Only return active subcontractors
        
        Returns:
            QuerySet of matching Subcontractor instances
        """
        queryset = SubcontractorSelector.get_base_queryset().filter(
            organization=organization
        ).filter(
            Q(name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(contact_person__icontains=query) |
            Q(email__icontains=query)
        )
        
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('name')


class SubcontractSelector:
    """
    Optimized selectors for subcontract agreement queries.
    """
    
    @staticmethod
    def get_base_queryset() -> QuerySet:
        """
        Get base queryset with common optimizations.
        
        Returns:
            Optimized QuerySet
        """
        return SubcontractAgreement.objects.select_related(
            'project',
            'project__organization',
            'subcontractor',
            'created_by'
        )
    
    @staticmethod
    def get_project_subcontracts(
        project,
        status: Optional[str] = None,
        include_draft: bool = False
    ) -> QuerySet:
        """
        Get all subcontracts for a project.
        
        Args:
            project: Project instance
            status: Filter by specific status (optional)
            include_draft: Whether to include DRAFT contracts
        
        Returns:
            QuerySet of SubcontractAgreement instances
        
        Example:
            # Get all active subcontracts
            active = SubcontractSelector.get_project_subcontracts(
                project=my_project,
                status=SubcontractAgreement.Status.ACTIVE
            )
        """
        queryset = SubcontractSelector.get_base_queryset().filter(
            project=project
        )
        
        if status:
            queryset = queryset.filter(status=status)
        elif not include_draft:
            queryset = queryset.exclude(status=SubcontractAgreement.Status.DRAFT)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_active_subcontracts(project) -> QuerySet:
        """
        Get active subcontracts for a project.
        
        Args:
            project: Project instance
        
        Returns:
            QuerySet of active SubcontractAgreement instances
        """
        return SubcontractSelector.get_project_subcontracts(
            project=project,
            status=SubcontractAgreement.Status.ACTIVE
        )
    
    @staticmethod
    def get_subcontract_with_claims(subcontract_id: str):
        """
        Get subcontract with all claims prefetched.
        
        Args:
            subcontract_id: UUID of subcontract
        
        Returns:
            SubcontractAgreement instance with claims prefetched
        """
        return SubcontractSelector.get_base_queryset().prefetch_related(
            'claims',
            'claims__submitted_by',
            'claims__certified_by'
        ).get(id=subcontract_id)
    
    @staticmethod
    def get_subcontract_summary(project) -> dict:
        """
        Get summary statistics for project subcontracts.
        
        Args:
            project: Project instance
        
        Returns:
            Dictionary with summary statistics
        
        Example:
            summary = SubcontractSelector.get_subcontract_summary(my_project)
            # {
            #     'total_contracts': 15,
            #     'active_contracts': 8,
            #     'total_contract_value': Decimal('25000000.00'),
            #     'total_certified': Decimal('12500000.00'),
            #     'total_paid': Decimal('10000000.00'),
            #     'avg_completion': Decimal('50.00')
            # }
        """
        contracts = SubcontractSelector.get_base_queryset().filter(
            project=project
        ).exclude(status=SubcontractAgreement.Status.DRAFT)
        
        stats = contracts.aggregate(
            total_contracts=Count('id'),
            active_contracts=Count(
                'id',
                filter=Q(status=SubcontractAgreement.Status.ACTIVE)
            ),
            total_contract_value=Coalesce(Sum('contract_value'), Decimal('0.00')),
        )
        
        # Calculate certified and paid amounts from claims
        from django.db.models import F
        
        certified_total = SubcontractClaim.objects.filter(
            subcontract__project=project,
            status__in=[
                SubcontractClaim.Status.CERTIFIED,
                SubcontractClaim.Status.PAID
            ]
        ).aggregate(
            total=Coalesce(Sum('certified_amount'), Decimal('0.00'))
        )['total']
        
        paid_total = SubcontractClaim.objects.filter(
            subcontract__project=project,
            status=SubcontractClaim.Status.PAID
        ).aggregate(
            total=Coalesce(Sum('certified_amount'), Decimal('0.00'))
        )['total']
        
        stats['total_certified'] = certified_total
        stats['total_paid'] = paid_total
        
        # Calculate average completion percentage
        if stats['total_contract_value'] > 0:
            stats['avg_completion'] = (
                certified_total / stats['total_contract_value']
            ) * Decimal('100')
        else:
            stats['avg_completion'] = Decimal('0.00')
        
        return stats
    
    @staticmethod
    def get_subcontractor_contracts(
        subcontractor,
        status: Optional[str] = None
    ) -> QuerySet:
        """
        Get all contracts for a specific subcontractor.
        
        Args:
            subcontractor: Subcontractor instance
            status: Filter by status (optional)
        
        Returns:
            QuerySet of SubcontractAgreement instances
        """
        queryset = SubcontractSelector.get_base_queryset().filter(
            subcontractor=subcontractor
        )
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')


class ClaimSelector:
    """
    Optimized selectors for subcontract claim queries.
    """
    
    @staticmethod
    def get_base_queryset() -> QuerySet:
        """
        Get base queryset with common optimizations.
        
        Returns:
            Optimized QuerySet
        """
        return SubcontractClaim.objects.select_related(
            'subcontract',
            'subcontract__project',
            'subcontract__subcontractor',
            'submitted_by',
            'certified_by',
            'created_by'
        )
    
    @staticmethod
    def get_subcontract_claims(
        subcontract,
        status: Optional[str] = None
    ) -> QuerySet:
        """
        Get all claims for a subcontract.
        
        Args:
            subcontract: SubcontractAgreement instance
            status: Filter by status (optional)
        
        Returns:
            QuerySet of SubcontractClaim instances
        
        Example:
            # Get all certified claims
            certified = ClaimSelector.get_subcontract_claims(
                subcontract=agreement,
                status=SubcontractClaim.Status.CERTIFIED
            )
        """
        queryset = ClaimSelector.get_base_queryset().filter(
            subcontract=subcontract
        )
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_project_claims(
        project,
        status: Optional[str] = None
    ) -> QuerySet:
        """
        Get all claims for a project across all subcontracts.
        
        Args:
            project: Project instance
            status: Filter by status (optional)
        
        Returns:
            QuerySet of SubcontractClaim instances
        """
        queryset = ClaimSelector.get_base_queryset().filter(
            subcontract__project=project
        )
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_pending_claims(project=None, organization=None) -> QuerySet:
        """
        Get all claims pending certification or payment.
        
        Args:
            project: Filter by project (optional)
            organization: Filter by organization (optional)
        
        Returns:
            QuerySet of pending SubcontractClaim instances
        
        Example:
            # Get all pending claims for a project
            pending = ClaimSelector.get_pending_claims(project=my_project)
            
            # Get all pending claims across organization
            all_pending = ClaimSelector.get_pending_claims(
                organization=my_org
            )
        """
        queryset = ClaimSelector.get_base_queryset().filter(
            status__in=[
                SubcontractClaim.Status.SUBMITTED,
                SubcontractClaim.Status.CERTIFIED
            ]
        )
        
        if project:
            queryset = queryset.filter(subcontract__project=project)
        
        if organization:
            queryset = queryset.filter(
                subcontract__project__organization=organization
            )
        
        return queryset.order_by('submitted_date')
    
    @staticmethod
    def get_claims_awaiting_certification(
        project=None,
        organization=None
    ) -> QuerySet:
        """
        Get claims submitted but not yet certified.
        
        Args:
            project: Filter by project (optional)
            organization: Filter by organization (optional)
        
        Returns:
            QuerySet of submitted SubcontractClaim instances
        """
        queryset = ClaimSelector.get_base_queryset().filter(
            status=SubcontractClaim.Status.SUBMITTED
        )
        
        if project:
            queryset = queryset.filter(subcontract__project=project)
        
        if organization:
            queryset = queryset.filter(
                subcontract__project__organization=organization
            )
        
        return queryset.order_by('submitted_date')
    
    @staticmethod
    def get_claims_awaiting_payment(
        project=None,
        organization=None
    ) -> QuerySet:
        """
        Get claims certified but not yet paid.
        
        Args:
            project: Filter by project (optional)
            organization: Filter by organization (optional)
        
        Returns:
            QuerySet of certified SubcontractClaim instances
        """
        queryset = ClaimSelector.get_base_queryset().filter(
            status=SubcontractClaim.Status.CERTIFIED
        )
        
        if project:
            queryset = queryset.filter(subcontract__project=project)
        
        if organization:
            queryset = queryset.filter(
                subcontract__project__organization=organization
            )
        
        return queryset.order_by('certified_date')
    
    @staticmethod
    def get_subcontract_payment_summary(subcontract) -> dict:
        """
        Get comprehensive payment summary for a subcontract.
        
        Args:
            subcontract: SubcontractAgreement instance
        
        Returns:
            Dictionary with payment summary
        
        Example:
            summary = ClaimSelector.get_subcontract_payment_summary(agreement)
            # {
            #     'contract_value': Decimal('5000000.00'),
            #     'total_claims': 5,
            #     'total_claimed': Decimal('3000000.00'),
            #     'total_certified': Decimal('2800000.00'),
            #     'total_retention': Decimal('280000.00'),
            #     'total_paid': Decimal('2000000.00'),
            #     'outstanding_certified': Decimal('800000.00'),
            #     'completion_percentage': Decimal('56.00'),
            #     'variance': Decimal('-200000.00'),
            #     'pending_certification_count': 1,
            #     'pending_payment_count': 2
            # }
        """
        claims = ClaimSelector.get_base_queryset().filter(
            subcontract=subcontract
        )
        
        # Aggregate claim statistics
        stats = claims.aggregate(
            total_claims=Count('id'),
            total_claimed=Coalesce(Sum('claimed_amount'), Decimal('0.00')),
            total_certified=Coalesce(
                Sum(
                    'certified_amount',
                    filter=Q(status__in=[
                        SubcontractClaim.Status.CERTIFIED,
                        SubcontractClaim.Status.PAID
                    ])
                ),
                Decimal('0.00')
            ),
            total_retention=Coalesce(
                Sum(
                    'retention_amount',
                    filter=Q(status__in=[
                        SubcontractClaim.Status.CERTIFIED,
                        SubcontractClaim.Status.PAID
                    ])
                ),
                Decimal('0.00')
            ),
            total_paid=Coalesce(
                Sum(
                    'certified_amount',
                    filter=Q(status=SubcontractClaim.Status.PAID)
                ),
                Decimal('0.00')
            ),
            pending_certification=Count(
                'id',
                filter=Q(status=SubcontractClaim.Status.SUBMITTED)
            ),
            pending_payment=Count(
                'id',
                filter=Q(status=SubcontractClaim.Status.CERTIFIED)
            )
        )
        
        # Add contract value
        stats['contract_value'] = subcontract.contract_value
        
        # Calculate derived values
        stats['outstanding_certified'] = (
            stats['total_certified'] - stats['total_paid']
        )
        
        if subcontract.contract_value > 0:
            stats['completion_percentage'] = (
                stats['total_certified'] / subcontract.contract_value
            ) * Decimal('100')
        else:
            stats['completion_percentage'] = Decimal('0.00')
        
        # Variance (certified vs claimed)
        stats['variance'] = stats['total_certified'] - stats['total_claimed']
        
        # Rename for clarity
        stats['pending_certification_count'] = stats.pop('pending_certification')
        stats['pending_payment_count'] = stats.pop('pending_payment')
        
        return stats
    
    @staticmethod
    def get_recent_claims(
        limit: int = 10,
        project=None,
        organization=None
    ) -> QuerySet:
        """
        Get most recently created claims.
        
        Args:
            limit: Maximum number of claims to return
            project: Filter by project (optional)
            organization: Filter by organization (optional)
        
        Returns:
            QuerySet of recent SubcontractClaim instances
        """
        queryset = ClaimSelector.get_base_queryset()
        
        if project:
            queryset = queryset.filter(subcontract__project=project)
        
        if organization:
            queryset = queryset.filter(
                subcontract__project__organization=organization
            )
        
        return queryset.order_by('-created_at')[:limit]
