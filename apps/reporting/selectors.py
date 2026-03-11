"""
Reporting Engine - Selectors

Optimized data queries for report generation with Pandas integration.
"""

import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import (
    Q, Sum, Avg, Count, Min, Max, F, Value,
    DecimalField, Case, When, OuterRef, Subquery
)
from django.db.models.functions import Coalesce, TruncDate, TruncMonth
from django.utils import timezone

from apps.reporting.models import Report, ReportSchedule, ReportExecution, ReportWidget
from apps.projects.models import Project
from apps.valuations.models import Valuation
from apps.variations.models import VariationOrder
from apps.subcontracts.models import SubcontractAgreement, SubcontractClaim
from apps.documents.models import Document
from apps.suppliers.models import LocalPurchaseOrder, SupplierInvoice
from apps.consultants.models import ConsultantPayment
from apps.ledger.models import Expense


class ReportSelector:
    """
    Selector for Report models.
    
    Provides optimized queries for report configurations.
    """
    
    @staticmethod
    def get_base_queryset():
        """Get base queryset with optimizations"""
        return Report.objects.select_related(
            'organization',
            'created_by'
        ).prefetch_related('schedules', 'executions')
    
    @staticmethod
    def get_active_reports(organization):
        """Get active  reports for organization"""
        return ReportSelector.get_base_queryset().filter(
            organization=organization,
            is_active=True
        )
    
    @staticmethod
    def get_public_reports(organization):
        """Get public reports available to all users"""
        return ReportSelector.get_active_reports(organization).filter(
            is_public=True
        )
    
    @staticmethod
    def get_user_reports(user):
        """Get reports created by or available to user"""
        return ReportSelector.get_base_queryset().filter(
            Q(organization=user.organization) &
            (Q(is_public=True) | Q(created_by=user))
        )


class ReportExecutionSelector:
    """
    Selector for ReportExecution models.
    
    Provides queries for execution history and results.
    """
    
    @staticmethod
    def get_base_queryset():
        """Get base queryset with optimizations"""
        return ReportExecution.objects.select_related(
            'report',
            'report__organization',
            'schedule',
            'executed_by'
        )
    
    @staticmethod
    def get_recent_executions(report, limit=10):
        """Get recent executions for a report"""
        return ReportExecutionSelector.get_base_queryset().filter(
            report=report
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_successful_executions(report):
        """Get successful executions"""
        return ReportExecutionSelector.get_base_queryset().filter(
            report=report,
            status__in=[ReportExecution.Status.COMPLETED, ReportExecution.Status.CACHED]
        )
    
    @staticmethod
    def get_cached_execution(cache_key):
        """Get execution by cache key"""
        return ReportExecution.objects.filter(
            cache_key=cache_key,
            status=ReportExecution.Status.CACHED
        ).first()


class ProjectFinancialDataSelector:
    """
    Selector for Project Financial Summary Report data.
    
    Aggregates financial data from multiple modules.
    """
    
    @staticmethod
    def get_project_summary(project, start_date=None, end_date=None):
        """
        Get comprehensive financial summary for a project.
        
        Returns:
            dict: Financial summary with all key metrics
        """
        # Base filters
        filters = {'project': project}
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date
        
        # Contract value (from project)
        contract_value = project.contract_value or Decimal('0.00')
        
        # Valuations (revenue recognized)
        valuations = Valuation.objects.filter(**filters).aggregate(
            total_certified=Coalesce(Sum('certified_amount'), Decimal('0.00')),
            total_paid=Coalesce(Sum('paid_amount'), Decimal('0.00')),
            retention_held=Coalesce(Sum('retention_amount'), Decimal('0.00'))
        )
        
        # Variations (contract changes)
        variations = VariationOrder.objects.filter(**filters).aggregate(
            approved_value=Coalesce(Sum(
                Case(
                    When(status='APPROVED', then=F('approved_amount')),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ), Decimal('0.00')),
            pending_value=Coalesce(Sum(
                Case(
                    When(status='PENDING', then=F('estimated_amount')),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ), Decimal('0.00'))
        )
        
        # Subcontractor costs
        subcontractor_costs = SubcontractClaim.objects.filter(
            subcontract__project=project
        ).aggregate(
            total_certified=Coalesce(Sum('certified_amount'), Decimal('0.00')),
            total_paid=Coalesce(Sum(
                Case(
                    When(status='PAID', then=F('net_payment_amount')),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ), Decimal('0.00'))
        )
        
        # Supplier costs
        supplier_costs = SupplierInvoice.objects.filter(
            purchase_order__project=project
        ).aggregate(
            total_invoiced=Coalesce(Sum('invoice_amount'), Decimal('0.00')),
            total_paid=Coalesce(Sum(
                Case(
                    When(status='PAID', then=F('invoice_amount')),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ), Decimal('0.00'))
        )
        
        # Consultant costs
        consultant_costs = ConsultantPayment.objects.filter(
            consultant_fee__project=project
        ).aggregate(
            total_paid=Coalesce(Sum('amount'), Decimal('0.00'))
        )
        
        # Other expenses
        other_expenses = Expense.objects.filter(
            allocations__project=project
        ).aggregate(
            total_amount=Coalesce(Sum('amount'), Decimal('0.00'))
        )
        
        # Calculate totals
        total_costs = (
            subcontractor_costs['total_certified'] +
            supplier_costs['total_invoiced'] +
            consultant_costs['total_paid'] +
            other_expenses['total_amount']
        )
        
        total_paid_costs = (
            subcontractor_costs['total_paid'] +
            supplier_costs['total_paid'] +
            consultant_costs['total_paid']
        )
        
        # Revised contract value
        revised_contract = contract_value + variations['approved_value']
        
        # Profit calculations
        gross_profit = valuations['total_certified'] - total_costs
        profit_margin = (
            (gross_profit / valuations['total_certified'] * 100)
            if valuations['total_certified'] > 0 else Decimal('0.00')
        )
        
        return {
            # Contract
            'contract_value': contract_value,
            'approved_variations': variations['approved_value'],
            'pending_variations': variations['pending_value'],
            'revised_contract_value': revised_contract,
            
            # Revenue
            'total_certified': valuations['total_certified'],
            'total_received': valuations['total_paid'],
            'retention_held': valuations['retention_held'],
            'outstanding_receivables': valuations['total_certified'] - valuations['total_paid'],
            
            # Costs
            'subcontractor_costs': subcontractor_costs['total_certified'],
            'supplier_costs': supplier_costs['total_invoiced'],
            'consultant_costs': consultant_costs['total_paid'],
            'other_expenses': other_expenses['total_amount'],
            'total_costs': total_costs,
            'total_paid_costs': total_paid_costs,
            'outstanding_payables': total_costs - total_paid_costs,
            
            # Profitability
            'gross_profit': gross_profit,
            'profit_margin': profit_margin,
            'completion_percentage': (
                (valuations['total_certified'] / revised_contract * 100)
                if revised_contract > 0 else Decimal('0.00')
            ),
            
            # Cash flow
            'net_cash_flow': valuations['total_paid'] - total_paid_costs,
        }
    
    @staticmethod
    def get_project_summary_dataframe(projects, start_date=None, end_date=None):
        """
        Get financial summary for multiple projects as Pandas DataFrame.
        
        Args:
            projects: QuerySet of Project objects
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            pd.DataFrame: Financial summary DataFrame
        """
        data = []
        for project in projects:
            summary = ProjectFinancialDataSelector.get_project_summary(
                project, start_date, end_date
            )
            summary['project_id'] = str(project.id)
            summary['project_name'] = project.name
            summary['project_code'] = project.code
            summary['project_status'] = project.status
            data.append(summary)
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Convert Decimal to float for Pandas compatibility
        numeric_cols = df.select_dtypes(include=['object']).columns
        for col in numeric_cols:
            if col not in ['project_id', 'project_name', 'project_code', 'project_status']:
                df[col] = pd.to_numeric(df[col], errors='ignore')
        
        return df


class CashFlowDataSelector:
    """
    Selector for Cash Flow Forecast Report data.
    """
    
    @staticmethod
    def get_cash_flow_forecast(project, months=12):
        """
        Get cash flow forecast for project.
        
        Args:
            project: Project object
            months: Number of months to forecast
        
        Returns:
            dict: Cash flow forecast data
        """
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30 * months)
        
        # Get scheduled valuations (revenue forecast)
        # This would integrate with the cashflow module
        # Placeholder implementation
        revenue_forecast = []
        
        # Get scheduled payments (expense forecast)
        expense_forecast = []
        
        # Subcontractor claims forecast
        pending_claims = SubcontractClaim.objects.filter(
            subcontract__project=project,
            status__in=['SUBMITTED', 'CERTIFIED']
        ).select_related('subcontract')
        
        for claim in pending_claims:
            expense_forecast.append({
                'date': claim.certified_date or claim.submitted_date,
                'description': f'Subcontractor: {claim.subcontract.subcontractor.name}',
                'amount': float(claim.net_payment_amount or claim.certified_amount or claim.claimed_amount),
                'category': 'Subcontractor'
            })
        
        # Supplier invoices forecast
        pending_invoices = SupplierInvoice.objects.filter(
            purchase_order__project=project,
            status='PENDING'
        ).select_related('purchase_order__supplier')
        
        for invoice in pending_invoices:
            expense_forecast.append({
                'date': invoice.due_date,
                'description': f'Supplier: {invoice.purchase_order.supplier.name}',
                'amount': float(invoice.invoice_amount),
                'category': 'Supplier'
            })
        
        return {
            'revenue_forecast': revenue_forecast,
            'expense_forecast': expense_forecast,
            'start_date': start_date,
            'end_date': end_date
        }


class VariationImpactDataSelector:
    """
    Selector for Variation Impact Report data.
    """
    
    @staticmethod
    def get_variation_summary(project):
        """Get variation orders summary for project"""
        variations = VariationOrder.objects.filter(project=project).select_related(
            'raised_by', 'approved_by'
        ).order_by('-created_at')
        
        summary = variations.aggregate(
            total_count=Count('id'),
            approved_count=Count(Case(When(status='APPROVED', then=1))),
            rejected_count=Count(Case(When(status='REJECTED', then=1))),
            pending_count=Count(Case(When(status='PENDING', then=1))),
            
            total_estimated=Coalesce(Sum('estimated_amount'), Decimal('0.00')),
            total_approved=Coalesce(Sum(
                Case(
                    When(status='APPROVED', then=F('approved_amount')),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ), Decimal('0.00')),
        )
        
        variations_df = pd.DataFrame(list(variations.values(
            'id', 'reference', 'title', 'status', 'estimated_amount',
            'approved_amount', 'created_at', 'approved_date'
        )))
        
        return {
            'summary': summary,
            'variations': variations,
            'dataframe': variations_df
        }


class SubcontractorPaymentDataSelector:
    """
    Selector for Subcontractor Payment Report data.
    """
    
    @staticmethod
    def get_subcontractor_payments(project=None, organization=None, start_date=None, end_date=None):
        """
        Get subcontractor payment summary.
        
        Returns comprehensive payment tracking data.
        """
        filters = {}
        if project:
            filters['subcontract__project'] = project
        elif organization:
            filters['subcontract__project__organization'] = organization
        
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date
        
        claims = SubcontractClaim.objects.filter(**filters).select_related(
            'subcontract',
            'subcontract__subcontractor',
            'subcontract__project',
            'submitted_by',
            'certified_by'
        ).order_by('-created_at')
        
        # Aggregate by subcontractor
        subcontractor_summary = {}
        for claim in claims:
            subcontractor = claim.subcontract.subcontractor
            key = str(subcontractor.id)
            
            if key not in subcontractor_summary:
                subcontractor_summary[key] = {
                    'subcontractor_id': key,
                    'subcontractor_name': subcontractor.name,
                    'total_claimed': Decimal('0.00'),
                    'total_certified': Decimal('0.00'),
                    'total_paid': Decimal('0.00'),
                    'outstanding': Decimal('0.00'),
                    'claim_count': 0
                }
            
            subcontractor_summary[key]['total_claimed'] += claim.claimed_amount
            subcontractor_summary[key]['total_certified'] += (claim.certified_amount or Decimal('0.00'))
            if claim.status == 'PAID':
                subcontractor_summary[key]['total_paid'] += (claim.net_payment_amount or Decimal('0.00'))
            subcontractor_summary[key]['claim_count'] += 1
        
        # Calculate outstanding
        for key in subcontractor_summary:
            summary = subcontractor_summary[key]
            summary['outstanding'] = summary['total_certified'] - summary['total_paid']
        
        df = pd.DataFrame(list(subcontractor_summary.values()))
        
        return {
            'claims': claims,
            'summary': list(subcontractor_summary.values()),
            'dataframe': df
        }


class DocumentAuditDataSelector:
    """
    Selector for Document Audit Report data.
    """
    
    @staticmethod
    def get_document_audit(project=None, organization=None, start_date=None, end_date=None):
        """
        Get document activity audit trail.
        
        Tracks document creation, updates, access, and signatures.
        """
        filters = {}
        if project:
            filters['project'] = project
        elif organization:
            filters['organization'] = organization
        
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date
        
        documents = Document.objects.filter(**filters).select_related(
            'uploaded_by',
            'project',
            'organization'
        ).prefetch_related(
            'signatures',
            'access_logs'
        ).order_by('-created_at')
        
        summary = documents.aggregate(
            total_count=Count('id'),
            total_signed=Count(Case(When(is_signed=True, then=1))),
            total_size=Coalesce(Sum('file_size'), 0)
        )
        
        # Group by document type
        by_type = documents.values('document_type').annotate(
            count=Count('id'),
            total_size=Sum('file_size')
        ).order_by('-count')
        
        df = pd.DataFrame(list(documents.values(
            'id', 'title', 'document_type', 'file_size',
            'is_signed', 'uploaded_by__username', 'created_at'
        )))
        
        return {
            'documents': documents,
            'summary': summary,
            'by_type': list(by_type),
            'dataframe': df
        }


class ProcurementDataSelector:
    """
    Selector for Procurement Summary Report data.
    """
    
    @staticmethod
    def get_procurement_summary(project=None, organization=None, start_date=None, end_date=None):
        """
        Get procurement summary with purchase orders and invoices.
        """
        filters = {}
        if project:
            filters['project'] = project
        elif organization:
            filters['project__organization'] = organization
        
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date
        
        # Purchase orders
        pos = LocalPurchaseOrder.objects.filter(**filters).select_related(
            'project',
            'supplier',
            'created_by'
        ).prefetch_related('invoices')
        
        po_summary = pos.aggregate(
            total_count=Count('id'),
            total_value=Coalesce(Sum('total_amount'), Decimal('0.00')),
            approved_count=Count(Case(When(status='APPROVED', then=1))),
            pending_count=Count(Case(When(status='PENDING', then=1)))
        )
        
        # Invoices
        invoice_filters = {k.replace('project__', 'purchase_order__project__'): v 
                          for k, v in filters.items()}
        
        invoices = SupplierInvoice.objects.filter(**invoice_filters).select_related(
            'purchase_order',
            'purchase_order__supplier'
        )
        
        invoice_summary = invoices.aggregate(
            total_count=Count('id'),
            total_invoiced=Coalesce(Sum('invoice_amount'), Decimal('0.00')),
            total_paid=Coalesce(Sum(
                Case(
                    When(status='PAID', then=F('invoice_amount')),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ), Decimal('0.00'))
        )
        
        # By supplier
        by_supplier = pos.values(
            'supplier__name'
        ).annotate(
            po_count=Count('id'),
            total_value=Sum('total_amount')
        ).order_by('-total_value')[:10]
        
        po_df = pd.DataFrame(list(pos.values(
            'id', 'po_number', 'supplier__name', 'total_amount',
            'status', 'created_at'
        )))
        
        return {
            'purchase_orders': pos,
            'invoices': invoices,
            'po_summary': po_summary,
            'invoice_summary': invoice_summary,
            'by_supplier': list(by_supplier),
            'dataframe': po_df
        }


class DashboardWidgetDataSelector:
    """
    Selector for dashboard widget data.
    """
    
    @staticmethod
    def get_widget_data(widget):
        """
        Get data for a specific widget based on its data_source.
        
        Args:
            widget: ReportWidget object
        
        Returns:
            dict: Widget data
        """
        organization = widget.organization
        params = widget.query_parameters or {}
        
        # Implement different data sources
        data_sources = {
            'project_count': lambda: Project.objects.filter(
                organization=organization
            ).count(),
            
            'active_project_count': lambda: Project.objects.filter(
                organization=organization,
                status='ACTIVE'
            ).count(),
            
            'total_contract_value': lambda: Project.objects.filter(
                organization=organization
            ).aggregate(
                total=Coalesce(Sum('contract_value'), Decimal('0.00'))
            )['total'],
            
            'total_revenue': lambda: Valuation.objects.filter(
                project__organization=organization
            ).aggregate(
                total=Coalesce(Sum('certified_amount'), Decimal('0.00'))
            )['total'],
            
            'pending_variations': lambda: VariationOrder.objects.filter(
                project__organization=organization,
                status='PENDING'
            ).count(),
            
            'outstanding_receivables': lambda: Valuation.objects.filter(
                project__organization=organization
            ).aggregate(
                total=Coalesce(
                    Sum(F('certified_amount') - F('paid_amount')),
                    Decimal('0.00')
                )
            )['total'],
        }
        
        data_source_func = data_sources.get(widget.data_source)
        if not data_source_func:
            return {'value': None, 'error': 'Unknown data source'}
        
        try:
            value = data_source_func()
            return {
                'value': value,
                'widget_type': widget.widget_type,
                'chart_type': widget.chart_type,
                'timestamp': timezone.now().isoformat()
            }
        except Exception as e:
            return {'value': None, 'error': str(e)}
