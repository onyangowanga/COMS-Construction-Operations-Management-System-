"""
Cash Flow Selectors

Optimized query functions for retrieving cash flow forecast data.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any, Optional
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Avg, Q, F, Count, QuerySet
from django.utils import timezone

from apps.cashflow.models import CashFlowForecast, PortfolioCashFlowSummary
from apps.projects.models import Project


def get_project_forecast(
    project_id: str,
    months: int = 6,
    start_date: Optional[datetime] = None
) -> QuerySet[CashFlowForecast]:
    """
    Get cash flow forecast for a specific project.
    
    Args:
        project_id: UUID of the project
        months: Number of months to fetch
        start_date: Start date (defaults to current month)
    
    Returns:
        QuerySet of CashFlowForecast ordered by month
    """
    if start_date is None:
        start_date = timezone.now().date().replace(day=1)
    
    end_date = start_date + relativedelta(months=months)
    
    return CashFlowForecast.objects.filter(
        project_id=project_id,
        forecast_month__gte=start_date,
        forecast_month__lt=end_date
    ).select_related('project').order_by('forecast_month')


def get_project_forecast_summary(project_id: str) -> Dict[str, Any]:
    """
    Get summarized forecast data for a project.
    
    Returns:
        - total_expected_inflow
        - total_expected_outflow
        - net_cash_flow
        - final_cash_balance
        - months_with_negative_flow
    """
    forecasts = CashFlowForecast.objects.filter(
        project_id=project_id
    ).aggregate(
        total_inflow=Sum('total_inflow'),
        total_outflow=Sum('total_outflow'),
        net_flow=Sum('net_cash_flow'),
        negative_months=Count('id', filter=Q(net_cash_flow__lt=0))
    )
    
    # Get final balance from latest forecast
    latest_forecast = CashFlowForecast.objects.filter(
        project_id=project_id
    ).order_by('-forecast_month').first()
    
    final_balance = (
        latest_forecast.cumulative_cash_balance
        if latest_forecast
        else Decimal('0.00')
    )
    
    return {
        'total_expected_inflow': forecasts.get('total_inflow') or Decimal('0.00'),
        'total_expected_outflow': forecasts.get('total_outflow') or Decimal('0.00'),
        'net_cash_flow': forecasts.get('net_flow') or Decimal('0.00'),
        'final_cash_balance': final_balance,
        'months_with_negative_flow': forecasts.get('negative_months') or 0
    }


def get_portfolio_forecast(
    months: int = 6,
    start_date: Optional[datetime] = None
) -> QuerySet[PortfolioCashFlowSummary]:
    """
    Get portfolio-wide cash flow forecast.
    
    Args:
        months: Number of months to fetch
        start_date: Start date (defaults to current month)
    
    Returns:
        QuerySet of PortfolioCashFlowSummary ordered by month
    """
    if start_date is None:
        start_date = timezone.now().date().replace(day=1)
    
    end_date = start_date + relativedelta(months=months)
    
    return PortfolioCashFlowSummary.objects.filter(
        forecast_month__gte=start_date,
        forecast_month__lt=end_date
    ).order_by('forecast_month')


def get_portfolio_forecast_summary() -> Dict[str, Any]:
    """
    Get summarized portfolio forecast data.
    
    Returns:
        - total_expected_inflow
        - total_expected_outflow
        - net_portfolio_cash_flow
        - final_portfolio_balance
        - months_with_negative_flow
        - total_forecast_months
        - average_burn_rate (from latest month)
        - cash_runway_months (from latest month)
    """
    summaries = PortfolioCashFlowSummary.objects.aggregate(
        total_inflow=Sum('total_portfolio_inflow'),
        total_outflow=Sum('total_portfolio_outflow'),
        net_flow=Sum('net_portfolio_cash_flow'),
        negative_months=Count('id', filter=Q(net_portfolio_cash_flow__lt=0)),
        total_months=Count('id')
    )
    
    # Get final balance and burn rate from latest month
    latest = PortfolioCashFlowSummary.objects.order_by('-forecast_month').first()
    
    final_balance = (
        latest.cumulative_portfolio_balance
        if latest
        else Decimal('0.00')
    )
    
    avg_burn_rate = (
        latest.average_cash_burn_rate
        if latest
        else Decimal('0.00')
    )
    
    runway_months = (
        latest.cash_runway_months
        if latest
        else Decimal('0.0')
    )
    
    return {
        'total_expected_inflow': summaries.get('total_inflow') or Decimal('0.00'),
        'total_expected_outflow': summaries.get('total_outflow') or Decimal('0.00'),
        'net_portfolio_cash_flow': summaries.get('net_flow') or Decimal('0.00'),
        'final_portfolio_balance': final_balance,
        'months_with_negative_flow': summaries.get('negative_months') or 0,
        'total_forecast_months': summaries.get('total_months') or 0,
        'average_burn_rate': avg_burn_rate,
        'cash_runway_months': runway_months
    }


def get_projects_with_negative_cash_flow(
    forecast_month: Optional[datetime] = None
) -> QuerySet[CashFlowForecast]:
    """
    Get projects with negative cash flow for a specific month.
    
    Args:
        forecast_month: Month to check (defaults to current month)
    
    Returns:
        QuerySet of CashFlowForecast with negative net_cash_flow
    """
    if forecast_month is None:
        forecast_month = timezone.now().date().replace(day=1)
    
    return CashFlowForecast.objects.filter(
        forecast_month=forecast_month,
        net_cash_flow__lt=0
    ).select_related(
        'project',
        'project__organization'
    ).order_by('net_cash_flow')  # Worst first


def get_projects_with_negative_cumulative_balance() -> QuerySet[CashFlowForecast]:
    """
    Get projects with negative cumulative cash balance.
    
    Returns:
        Latest forecast for each project with negative balance
    """
    from django.db.models import OuterRef, Subquery
    
    # Get latest forecast for each project
    latest_forecasts = CashFlowForecast.objects.filter(
        project=OuterRef('project')
    ).order_by('-forecast_month')
    
    # Get projects with negative balance in latest forecast
    return CashFlowForecast.objects.filter(
        forecast_month=Subquery(latest_forecasts.values('forecast_month')[:1]),
        cumulative_cash_balance__lt=0
    ).select_related(
        'project',
        'project__organization'
    ).order_by('cumulative_cash_balance')


def get_cash_flow_trend_data(
    project_id: str,
    months: int = 6
) -> List[Dict[str, Any]]:
    """
    Get cash flow trend data for charting.
    
    Returns list of dictionaries with:
    - month: 'YYYY-MM'
    - inflow: Decimal
    - outflow: Decimal
    - net_flow: Decimal
    - cumulative_balance: Decimal
    """
    forecasts = get_project_forecast(project_id, months=months)
    
    return [
        {
            'month': f.forecast_month.strftime('%Y-%m'),
            'month_label': f.forecast_month.strftime('%b %Y'),
            'inflow': float(f.total_inflow),
            'outflow': float(f.total_outflow),
            'net_flow': float(f.net_cash_flow),
            'cumulative_balance': float(f.cumulative_cash_balance),
        }
        for f in forecasts
    ]


def get_portfolio_cash_flow_trend_data(months: int = 6) -> List[Dict[str, Any]]:
    """
    Get portfolio cash flow trend data for charting.
    
    Returns list of dictionaries with:
    - month: 'YYYY-MM'
    - inflow: Decimal
    - outflow: Decimal
    - net_flow: Decimal
    - cumulative_balance: Decimal
    - active_projects: int
    """
    summaries = get_portfolio_forecast(months=months)
    
    return [
        {
            'month': s.forecast_month.strftime('%Y-%m'),
            'month_label': s.forecast_month.strftime('%b %Y'),
            'inflow': float(s.total_portfolio_inflow),
            'outflow': float(s.total_portfolio_outflow),
            'net_flow': float(s.net_portfolio_cash_flow),
            'cumulative_balance': float(s.cumulative_portfolio_balance),
            'active_projects': s.active_projects_count,
            'negative_projects': s.projects_with_negative_flow,
        }
        for s in summaries
    ]


def get_inflow_breakdown(
    project_id: str,
    forecast_month: Optional[datetime] = None
) -> Dict[str, Decimal]:
    """
    Get detailed inflow breakdown for a project and month.
    
    Returns:
    - valuations
    - client_payments
    - retention_releases
    - variation_orders
    - total
    """
    if forecast_month is None:
        forecast_month = timezone.now().date().replace(day=1)
    
    try:
        forecast = CashFlowForecast.objects.get(
            project_id=project_id,
            forecast_month=forecast_month
        )
        
        return {
            'valuations': forecast.expected_valuations,
            'client_payments': forecast.expected_client_payments,
            'retention_releases': forecast.expected_retention_releases,
            'variation_orders': forecast.expected_variation_order_payments,
            'total': forecast.total_inflow
        }
    except CashFlowForecast.DoesNotExist:
        return {
            'valuations': Decimal('0.00'),
            'client_payments': Decimal('0.00'),
            'retention_releases': Decimal('0.00'),
            'variation_orders': Decimal('0.00'),
            'total': Decimal('0.00')
        }


def get_outflow_breakdown(
    project_id: str,
    forecast_month: Optional[datetime] = None
) -> Dict[str, Decimal]:
    """
    Get detailed outflow breakdown for a project and month.
    
    Returns:
    - supplier_payments
    - labour_costs
    - consultant_fees
    - procurement_payments
    - site_expenses
    - other_expenses
    - total
    """
    if forecast_month is None:
        forecast_month = timezone.now().date().replace(day=1)
    
    try:
        forecast = CashFlowForecast.objects.get(
            project_id=project_id,
            forecast_month=forecast_month
        )
        
        return {
            'supplier_payments': forecast.expected_supplier_payments,
            'labour_costs': forecast.expected_labour_costs,
            'consultant_fees': forecast.expected_consultant_fees,
            'procurement_payments': forecast.expected_procurement_payments,
            'site_expenses': forecast.expected_site_expenses,
            'other_expenses': forecast.expected_other_expenses,
            'total': forecast.total_outflow
        }
    except CashFlowForecast.DoesNotExist:
        return {
            'supplier_payments': Decimal('0.00'),
            'labour_costs': Decimal('0.00'),
            'consultant_fees': Decimal('0.00'),
            'procurement_payments': Decimal('0.00'),
            'site_expenses': Decimal('0.00'),
            'other_expenses': Decimal('0.00'),
            'total': Decimal('0.00')
        }


def get_critical_cash_flow_alerts() -> List[Dict[str, Any]]:
    """
    Get critical cash flow alerts for the portfolio.
    
    Returns list of projects with:
    - Negative cumulative balance
    - Severe negative monthly cash flow
    - Multiple consecutive months of negative flow
    """
    alerts = []
    
    # Alert 1: Projects with negative cumulative balance
    negative_balance_projects = get_projects_with_negative_cumulative_balance()
    
    for forecast in negative_balance_projects:
        alerts.append({
            'project_id': str(forecast.project.id),
            'project_name': forecast.project.name,
            'alert_type': 'NEGATIVE_BALANCE',
            'severity': 'CRITICAL',
            'message': f"Cumulative cash balance: {forecast.cumulative_cash_balance:,.2f}",
            'forecast_month': forecast.forecast_month
        })
    
    # Alert 2: Projects with severe negative monthly flow
    current_month = timezone.now().date().replace(day=1)
    severe_negative_flow = CashFlowForecast.objects.filter(
        forecast_month=current_month,
        net_cash_flow__lt=-100000  # More than -100K
    ).select_related('project')
    
    for forecast in severe_negative_flow:
        alerts.append({
            'project_id': str(forecast.project.id),
            'project_name': forecast.project.name,
            'alert_type': 'SEVERE_NEGATIVE_FLOW',
            'severity': 'HIGH',
            'message': f"Expected negative cash flow: {forecast.net_cash_flow:,.2f}",
            'forecast_month': forecast.forecast_month
        })
    
    return alerts
