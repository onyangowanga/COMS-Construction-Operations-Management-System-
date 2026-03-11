"""
Cash Flow Forecasting Service

Computes cash flow forecasts for construction projects based on:
- Valuation schedules and payment histories
- Expense patterns and procurement schedules
- Historical cash flow trends
"""

from decimal import Decimal
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Any, Optional
from django.db.models import Sum, Avg, Q, F
from django.db import transaction
from django.utils import timezone

from apps.projects.models import Project
from apps.valuations.models import Valuation
from apps.ledger.models import Expense
from apps.cashflow.models import CashFlowForecast, PortfolioCashFlowSummary


class CashFlowService:
    """Service for computing and managing cash flow forecasts"""
    
    # Forecast horizons (in months)
    HORIZON_SHORT = 3
    HORIZON_MEDIUM = 6
    HORIZON_LONG = 12
    
    # Payment delay assumptions (days)
    CLIENT_PAYMENT_DELAY_DAYS = 30  # Typical client payment delay
    SUPPLIER_PAYMENT_DELAY_DAYS = 30  # Typical supplier payment delay
    
    # Default retention percentage
    DEFAULT_RETENTION_RATE = Decimal('0.05')  # 5%
    
    @staticmethod
    @transaction.atomic
    def generate_project_forecast(
        project_id: str,
        horizon_months: int = 6,
        start_date: Optional[datetime] = None
    ) -> List[CashFlowForecast]:
        """
        Generate cash flow forecast for a single project.
        
        Args:
            project_id: UUID of the project
            horizon_months: Number of months to forecast (3, 6, or 12)
            start_date: Start date for forecast (defaults to current month)
        
        Returns:
            List of CashFlowForecast instances
        
        Business Logic:
        - Analyzes historical valuation and expense patterns
        - Projects future inflows based on contract progress
        - Projects future outflows based on expense trends
        - Computes cumulative balances
        """
        project = Project.objects.select_related('organization').get(id=project_id)
        
        if start_date is None:
            start_date = timezone.now().date().replace(day=1)
        
        # Delete existing forecasts for this period
        CashFlowForecast.objects.filter(
            project=project,
            forecast_month__gte=start_date
        ).delete()
        
        forecasts = []
        cumulative_balance = CashFlowService._get_current_cash_balance(project)
        
        for month_offset in range(horizon_months):
            forecast_month = start_date + relativedelta(months=month_offset)
            
            # Compute inflows for this month
            inflows = CashFlowService._compute_monthly_inflows(
                project, forecast_month
            )
            
            # Compute outflows for this month
            outflows = CashFlowService._compute_monthly_outflows(
                project, forecast_month
            )
            
            # Calculate cumulative balance
            net_flow = (
                inflows['total_inflow'] - outflows['total_outflow']
            )
            cumulative_balance += net_flow
            
            # Calculate confidence level for this forecast
            confidence_level = CashFlowService._calculate_confidence_level(
                project, forecast_month
            )
            
            # Create forecast record
            forecast = CashFlowForecast.objects.create(
                project=project,
                forecast_month=forecast_month,
                # Inflows
                expected_valuations=inflows['valuations'],
                expected_client_payments=inflows['client_payments'],
                expected_retention_releases=inflows['retention_releases'],
                expected_variation_order_payments=inflows['variation_orders'],
                total_inflow=inflows['total_inflow'],
                # Outflows
                expected_supplier_payments=outflows['supplier_payments'],
                expected_labour_costs=outflows['labour_costs'],
                expected_consultant_fees=outflows['consultant_fees'],
                expected_procurement_payments=outflows['procurement_payments'],
                expected_site_expenses=outflows['site_expenses'],
                expected_other_expenses=outflows['other_expenses'],
                total_outflow=outflows['total_outflow'],
                # Metrics
                net_cash_flow=net_flow,
                cumulative_cash_balance=cumulative_balance,
                confidence_level=confidence_level,
                is_actual=False
            )
            
            forecasts.append(forecast)
        
        return forecasts
    
    @staticmethod
    def _get_current_cash_balance(project: Project) -> Decimal:
        """
        Calculate current cash balance for a project.
        
        Returns: Total client payments received - Total expenses paid
        """
        # Get total approved valuations (revenue)
        total_revenue = Valuation.objects.filter(
            project=project,
            status='APPROVED'
        ).aggregate(
            total=Sum('work_completed_value')
        )['total'] or Decimal('0.00')
        
        # Get total approved expenses
        total_expenses = Expense.objects.filter(
            project=project,
            status='APPROVED'
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Simplified balance (in reality, would track actual payments)
        return total_revenue - total_expenses
    
    @staticmethod
    def _compute_monthly_inflows(
        project: Project,
        forecast_month: datetime
    ) -> Dict[str, Decimal]:
        """
        Compute expected inflows for a specific month.
        
        Inflow Sources:
        1. Valuations: Based on project progress and schedule
        2. Client Payments: Expected payments on approved valuations
        3. Retention Releases: Scheduled retention releases
        4. Variation Orders: Approved variation order payments
        """
        # Get project progress metrics
        contract_value = project.contract_sum or Decimal('0.00')
        
        # Get cumulative progress
        approved_valuations = Valuation.objects.filter(
            project=project,
            status='APPROVED'
        ).aggregate(
            total=Sum('work_completed_value')
        )['total'] or Decimal('0.00')
        
        # Calculate progress percentage
        if contract_value > 0:
            progress = (approved_valuations / contract_value) * 100
        else:
            progress = Decimal('0.00')
        
        # === 1. Expected Valuations ===
        # Estimate based on remaining work and project duration
        remaining_value = contract_value - approved_valuations
        
        if remaining_value < 0:
            remaining_value = Decimal('0.00')
        
        # Get project timeline
        months_remaining = CashFlowService._get_months_remaining(
            project, forecast_month
        )
        
        if months_remaining > 0:
            # Distribute remaining value over remaining months
            monthly_valuation = remaining_value / Decimal(months_remaining)
            
            # Apply S-curve weighting (more work in middle months)
            if progress < 20:
                monthly_valuation *= Decimal('0.7')  # Slow start
            elif progress > 80:
                monthly_valuation *= Decimal('0.5')  # Slow finish
        else:
            monthly_valuation = Decimal('0.00')
        
        # === 2. Expected Client Payments ===
        # Based on valuations from previous month (payment delay)
        previous_month = forecast_month - relativedelta(months=1)
        
        # Get valuations approved in previous months
        recent_valuations = Valuation.objects.filter(
            project=project,
            status='APPROVED',
            approval_date__year=previous_month.year,
            approval_date__month=previous_month.month
        ).aggregate(
            total=Sum('work_completed_value')
        )['total'] or Decimal('0.00')
        
        # Expected payment (less retention)
        retention_rate = CashFlowService.DEFAULT_RETENTION_RATE
        expected_payment = recent_valuations * (Decimal('1.00') - retention_rate)
        
        # === 3. Retention Releases ===
        # Check if project is near completion
        retention_release = Decimal('0.00')
        
        if progress > 95:  # Near completion
            # Release accumulated retention
            total_retention = approved_valuations * retention_rate
            retention_release = total_retention / Decimal('3')  # Over 3 months
        
        # === 4. Variation Order Payments ===
        # Simplified: assume 10% of variations paid monthly
        variation_payments = Decimal('0.00')  # Would query variation orders
        
        # Total inflows
        total_inflow = (
            monthly_valuation +
            expected_payment +
            retention_release +
            variation_payments
        )
        
        return {
            'valuations': monthly_valuation,
            'client_payments': expected_payment,
            'retention_releases': retention_release,
            'variation_orders': variation_payments,
            'total_inflow': total_inflow
        }
    
    @staticmethod
    def _compute_monthly_outflows(
        project: Project,
        forecast_month: datetime
    ) -> Dict[str, Decimal]:
        """
        Compute expected outflows for a specific month.
        
        Outflow Sources:
        1. Supplier Payments: Based on procurement and expense patterns
        2. Labour Costs: Based on historical payroll data
        3. Consultant Fees: Based on contract schedules
        4. Procurement Payments: Based on pending orders
        5. Site Expenses: Based on historical site costs
        """
        # Get average monthly expenses from last 3 months
        three_months_ago = forecast_month - relativedelta(months=3)
        
        historical_expenses = Expense.objects.filter(
            project=project,
            date__gte=three_months_ago,
            date__lt=forecast_month,
            status='APPROVED'
        ).aggregate(
            avg_monthly=Avg('amount'),
            total=Sum('amount')
        )
        
        avg_monthly_expense = historical_expenses.get('avg_monthly') or Decimal('0.00')
        
        # === 1. Supplier Payments ===
        # Get pending supplier invoices (simplified)
        supplier_payments = avg_monthly_expense * Decimal('0.40')  # 40% typically suppliers
        
        # === 2. Labour Costs ===
        # Based on historical labour expenses
        labour_costs = avg_monthly_expense * Decimal('0.30')  # 30% typically labour
        
        # === 3. Consultant Fees ===
        # Typically 5-10% of monthly expenses
        consultant_fees = avg_monthly_expense * Decimal('0.10')
        
        # === 4. Procurement Payments ===
        # Based on pending procurement orders
        procurement_payments = avg_monthly_expense * Decimal('0.10')
        
        # === 5. Site Expenses ===
        # Utilities, equipment rental, etc.
        site_expenses = avg_monthly_expense * Decimal('0.08')
        
        # === 6. Other Expenses ===
        other_expenses = avg_monthly_expense * Decimal('0.02')
        
        # Total outflows
        total_outflow = (
            supplier_payments +
            labour_costs +
            consultant_fees +
            procurement_payments +
            site_expenses +
            other_expenses
        )
        
        return {
            'supplier_payments': supplier_payments,
            'labour_costs': labour_costs,
            'consultant_fees': consultant_fees,
            'procurement_payments': procurement_payments,
            'site_expenses': site_expenses,
            'other_expenses': other_expenses,
            'total_outflow': total_outflow
        }
    
    @staticmethod
    def _get_months_remaining(project: Project, current_date: datetime) -> int:
        """Calculate months remaining until project end date"""
        if not project.end_date:
            return 12  # Default assumption
        
        end_date = project.end_date
        
        if isinstance(current_date, datetime):
            current_date = current_date.date()
        
        months_remaining = (
            (end_date.year - current_date.year) * 12 +
            (end_date.month - current_date.month)
        )
        
        return max(months_remaining, 1)  # At least 1 month
    
    @staticmethod
    def _calculate_confidence_level(
        project: Project,
        forecast_month: datetime
    ) -> str:
        """
        Calculate forecast confidence level based on multiple factors.
        
        Confidence Factors:
        1. Project Progress (Primary) - More progress = more historical data
        2. Historical Data Availability - More expense records = better predictions
        3. Cost Variance - Lower variance = more predictable
        
        Returns:
            'LOW', 'MEDIUM', or 'HIGH'
        """
        # === Factor 1: Project Progress ===
        contract_value = project.contract_sum or Decimal('0.00')
        
        if contract_value > 0:
            approved_valuations = Valuation.objects.filter(
                project=project,
                status='APPROVED'
            ).aggregate(total=Sum('work_completed_value'))['total'] or Decimal('0.00')
            
            progress_percentage = (approved_valuations / contract_value * 100)
        else:
            progress_percentage = Decimal('0')
        
        # Base confidence from user specification
        if progress_percentage < 20:
            base_confidence = 'LOW'
        elif progress_percentage < 60:
            base_confidence = 'MEDIUM'
        else:
            base_confidence = 'HIGH'
        
        # === Factor 2: Historical Data Availability ===
        expense_count = Expense.objects.filter(
            project=project,
            status='APPROVED'
        ).count()
        
        # Downgrade confidence if insufficient historical data
        if expense_count < 10 and base_confidence == 'HIGH':
            base_confidence = 'MEDIUM'
        elif expense_count < 5 and base_confidence == 'MEDIUM':
            base_confidence = 'LOW'
        
        # === Factor 3: Cost Variance (Optional - if portfolio metrics exist) ===
        try:
            # Try to import portfolio metrics if available
            from apps.portfolio.models import ProjectMetrics
            
            metrics = ProjectMetrics.objects.filter(project=project).first()
            
            if metrics and hasattr(metrics, 'cost_performance_index'):
                cpi = float(metrics.cost_performance_index)
                variance = abs(cpi - 1.0)
                
                # High variance reduces confidence
                if variance > 0.3 and base_confidence == 'HIGH':
                    base_confidence = 'MEDIUM'
        except (ImportError, Exception):
            # Portfolio module doesn't exist or has different structure
            pass
        
        return base_confidence
    
    @staticmethod
    @transaction.atomic
    def generate_portfolio_forecast(
        horizon_months: int = 6,
        start_date: Optional[datetime] = None
    ) -> List[PortfolioCashFlowSummary]:
        """
        Generate portfolio-wide cash flow forecast.
        
        Args:
            horizon_months: Number of months to forecast
            start_date: Start date for forecast
        
        Returns:
            List of PortfolioCashFlowSummary instances
        """
        if start_date is None:
            start_date = timezone.now().date().replace(day=1)
        
        # Get all active projects
        active_projects = Project.objects.filter(
            status__in=['DESIGN', 'APPROVAL', 'IMPLEMENTATION', 'ON_HOLD']
        )
        
        # Generate forecasts for each project
        for project in active_projects:
            try:
                CashFlowService.generate_project_forecast(
                    project_id=str(project.id),
                    horizon_months=horizon_months,
                    start_date=start_date
                )
            except Exception as e:
                print(f"Error forecasting project {project.name}: {e}")
                continue
        
        # Delete existing portfolio summaries for this period
        PortfolioCashFlowSummary.objects.filter(
            forecast_month__gte=start_date
        ).delete()
        
        # Aggregate portfolio summaries
        summaries = []
        cumulative_balance = Decimal('0.00')
        
        # Calculate average burn rate across the forecast period
        all_monthly_outflows = []
        
        for month_offset in range(horizon_months):
            forecast_month = start_date + relativedelta(months=month_offset)
            
            # Aggregate all project forecasts for this month
            monthly_forecasts = CashFlowForecast.objects.filter(
                forecast_month=forecast_month
            ).aggregate(
                total_inflow=Sum('total_inflow'),
                total_outflow=Sum('total_outflow'),
                net_flow=Sum('net_cash_flow')
            )
            
            total_inflow = monthly_forecasts.get('total_inflow') or Decimal('0.00')
            total_outflow = monthly_forecasts.get('total_outflow') or Decimal('0.00')
            net_flow = monthly_forecasts.get('net_flow') or Decimal('0.00')
            
            cumulative_balance += net_flow
            all_monthly_outflows.append(total_outflow)
            
            # Count projects with negative cash flow
            negative_flow_count = CashFlowForecast.objects.filter(
                forecast_month=forecast_month,
                net_cash_flow__lt=0
            ).count()
            
            # Calculate average cash burn rate
            if all_monthly_outflows:
                avg_burn_rate = sum(all_monthly_outflows) / Decimal(len(all_monthly_outflows))
            else:
                avg_burn_rate = Decimal('0.00')
            
            # Calculate runway months
            if avg_burn_rate > 0:
                # Use cumulative balance to estimate runway
                cash_runway = cumulative_balance / avg_burn_rate
            else:
                cash_runway = Decimal('999.9')  # Infinite runway
            
            # Create portfolio summary
            summary = PortfolioCashFlowSummary.objects.create(
                forecast_month=forecast_month,
                total_portfolio_inflow=total_inflow,
                total_portfolio_outflow=total_outflow,
                net_portfolio_cash_flow=net_flow,
                cumulative_portfolio_balance=cumulative_balance,
                active_projects_count=active_projects.count(),
                projects_with_negative_flow=negative_flow_count,
                average_cash_burn_rate=avg_burn_rate,
                cash_runway_months=cash_runway
            )
            
            summaries.append(summary)
        
        return summaries
    
    @staticmethod
    def update_all_forecasts(horizon_months: int = 6) -> Dict[str, int]:
        """
        Update forecasts for all active projects.
        
        Returns:
            Dictionary with update statistics
        """
        # Generate portfolio forecast (includes all projects)
        summaries = CashFlowService.generate_portfolio_forecast(
            horizon_months=horizon_months
        )
        
        # Count updated projects
        updated_projects = CashFlowForecast.objects.values('project').distinct().count()
        
        return {
            'updated_projects': updated_projects,
            'forecast_months': len(summaries),
            'horizon_months': horizon_months
        }
