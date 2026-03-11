"""
Portfolio Analytics Service Layer
Business logic for computing portfolio metrics, risk indicators, and EVM
"""
from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.db.models import Sum, Count, Q, F
from django.utils import timezone

from apps.portfolio.models import ProjectMetrics
from apps.projects.models import Project
from apps.ledger.models import Expense
from apps.clients.models import ClientPayment
from apps.valuations.models import Valuation


class PortfolioAnalyticsService:
    """Service for portfolio analytics and project metrics computation"""
    
    @staticmethod
    @transaction.atomic
    def compute_project_risk_indicators(project_id: str) -> ProjectMetrics:
        """
        Compute comprehensive risk indicators and performance metrics for a project
        
        Args:
            project_id: UUID of the project
        
        Returns:
            ProjectMetrics instance with updated values
        
        Business Rules:
            - Budget utilization > 90% = WARNING
            - Budget utilization > 100% = CRITICAL (over budget)
            - CPI < 0.9 = HIGH RISK (cost overrun)
            - SPI < 0.9 = HIGH RISK (schedule delay)
            - Profit margin < 0 = CRITICAL
            - Profit margin < 5% = WARNING
        """
        project = Project.objects.get(id=project_id)
        
        # Get or create metrics instance
        metrics, created = ProjectMetrics.objects.get_or_create(project=project)
        
        # 1. Calculate Financial Metrics
        total_contract_value = project.project_value or Decimal('0.00')
        
        # Total approved expenses
        total_expenses = Expense.objects.filter(
            project=project,
            approval_status='APPROVED'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Total revenue (client payments)
        total_revenue = ClientPayment.objects.filter(
            project=project
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Profit calculation
        total_profit = total_revenue - total_expenses
        
        # Budget utilization percentage
        budget_utilization = Decimal('0.00')
        if total_contract_value > 0:
            budget_utilization = (total_expenses / total_contract_value) * 100
        
        # Profit margin percentage
        profit_margin = Decimal('0.00')
        if total_revenue > 0:
            profit_margin = (total_profit / total_revenue) * 100
        
        # 2. Compute Earned Value Metrics
        evm_metrics = PortfolioAnalyticsService._compute_earned_value_metrics(project)
        
        # 3. Compute Schedule Metrics
        schedule_metrics = PortfolioAnalyticsService._compute_schedule_metrics(project)
        
        # 4. Determine Risk Level
        risk_level = PortfolioAnalyticsService._determine_risk_level(
            budget_utilization=budget_utilization,
            profit_margin=profit_margin,
            cpi=evm_metrics['cost_performance_index'],
            spi=evm_metrics['schedule_performance_index']
        )
        
        # 5. Determine Project Health
        project_health = PortfolioAnalyticsService._determine_project_health(
            risk_level=risk_level,
            budget_utilization=budget_utilization,
            profit_margin=profit_margin,
            is_behind_schedule=schedule_metrics['is_behind_schedule']
        )
        
        # 6. Update metrics
        metrics.total_contract_value = total_contract_value
        metrics.total_expenses = total_expenses
        metrics.total_revenue = total_revenue
        metrics.total_profit = total_profit
        metrics.budget_utilization = budget_utilization
        metrics.profit_margin = profit_margin
        
        # EVM metrics
        metrics.planned_value = evm_metrics['planned_value']
        metrics.earned_value = evm_metrics['earned_value']
        metrics.actual_cost = evm_metrics['actual_cost']
        metrics.cost_performance_index = evm_metrics['cost_performance_index']
        metrics.schedule_performance_index = evm_metrics['schedule_performance_index']
        
        # Schedule metrics
        metrics.days_elapsed = schedule_metrics['days_elapsed']
        metrics.days_remaining = schedule_metrics['days_remaining']
        metrics.schedule_variance_days = schedule_metrics['schedule_variance_days']
        
        # Risk and health
        metrics.risk_level = risk_level
        metrics.project_health = project_health
        
        # Flags
        metrics.is_over_budget = total_expenses > total_contract_value if total_contract_value > 0 else False
        metrics.is_behind_schedule = schedule_metrics['is_behind_schedule']
        
        metrics.save()
        
        return metrics
    
    @staticmethod
    def _compute_earned_value_metrics(project: Project) -> Dict[str, Decimal]:
        """
        Compute Earned Value Management (EVM) metrics
        
        EVM Metrics:
            - PV (Planned Value): Budget allocated for scheduled work
            - EV (Earned Value): Budget allocated for work actually performed
            - AC (Actual Cost): Actual expenses incurred
            - CPI (Cost Performance Index): EV / AC (>1 good, <1 over budget)
            - SPI (Schedule Performance Index): EV / PV (>1 ahead, <1 behind)
        
        Returns:
            Dictionary with EVM metrics
        """
        total_contract_value = project.project_value or Decimal('0.00')
        
        # Actual Cost = Total approved expenses
        actual_cost = Expense.objects.filter(
            project=project,
            approval_status='APPROVED'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Earned Value = Total work certified in valuations
        # Use the latest approved valuation's work_completed_value
        latest_valuation = Valuation.objects.filter(
            project=project,
            status__in=['APPROVED', 'PAID']
        ).order_by('-valuation_date').first()
        
        earned_value = Decimal('0.00')
        if latest_valuation:
            earned_value = latest_valuation.work_completed_value
        
        # Planned Value = Expected progress based on schedule
        # Calculate as: (days_elapsed / total_days) * contract_value
        planned_value = Decimal('0.00')
        if project.start_date and project.end_date and total_contract_value > 0:
            today = date.today()
            total_days = (project.end_date - project.start_date).days
            
            if total_days > 0:
                if today >= project.end_date:
                    # Project should be complete
                    planned_value = total_contract_value
                elif today >= project.start_date:
                    # Project is in progress
                    days_elapsed = (today - project.start_date).days
                    progress_percentage = Decimal(str(days_elapsed)) / Decimal(str(total_days))
                    planned_value = total_contract_value * progress_percentage
                # else: Project hasn't started, PV = 0
        
        # Calculate indices (avoid division by zero)
        cost_performance_index = Decimal('1.00')
        if actual_cost > 0:
            cost_performance_index = earned_value / actual_cost
        
        schedule_performance_index = Decimal('1.00')
        if planned_value > 0:
            schedule_performance_index = earned_value / planned_value
        
        return {
            'planned_value': planned_value,
            'earned_value': earned_value,
            'actual_cost': actual_cost,
            'cost_performance_index': cost_performance_index,
            'schedule_performance_index': schedule_performance_index,
        }
    
    @staticmethod
    def _compute_schedule_metrics(project: Project) -> Dict[str, Any]:
        """
        Compute schedule-related metrics
        
        Returns:
            Dictionary with schedule metrics
        """
        today = date.today()
        
        days_elapsed = 0
        days_remaining = 0
        schedule_variance_days = 0
        is_behind_schedule = False
        
        if project.start_date and project.end_date:
            # Calculate days elapsed
            if today >= project.start_date:
                days_elapsed = (today - project.start_date).days
            
            # Calculate days remaining
            if today <= project.end_date:
                days_remaining = (project.end_date - today).days
            else:
                days_remaining = 0  # Project overdue
                is_behind_schedule = True
            
            # Schedule variance (based on SPI if available)
            total_days = (project.end_date - project.start_date).days
            if total_days > 0:
                expected_days = days_elapsed
                
                # Get actual progress from valuations
                latest_valuation = Valuation.objects.filter(
                    project=project,
                    status__in=['APPROVED', 'PAID']
                ).order_by('-valuation_date').first()
                
                if latest_valuation and project.project_value and project.project_value > 0:
                    actual_progress_pct = (
                        latest_valuation.work_completed_value / project.project_value
                    )
                    actual_days_equivalent = int(total_days * actual_progress_pct)
                    schedule_variance_days = actual_days_equivalent - expected_days
                    
                    if schedule_variance_days < 0:
                        is_behind_schedule = True
        
        return {
            'days_elapsed': days_elapsed,
            'days_remaining': days_remaining,
            'schedule_variance_days': schedule_variance_days,
            'is_behind_schedule': is_behind_schedule,
        }
    
    @staticmethod
    def _determine_risk_level(
        budget_utilization: Decimal,
        profit_margin: Decimal,
        cpi: Decimal,
        spi: Decimal
    ) -> str:
        """
        Determine project risk level based on multiple indicators
        
        Risk Levels:
            - CRITICAL: Major issues requiring immediate action
            - HIGH: Significant issues requiring attention
            - MEDIUM: Some concerns, monitoring needed
            - LOW: On track, minimal concerns
        
        Args:
            budget_utilization: Percentage of budget used
            profit_margin: Profit margin percentage
            cpi: Cost Performance Index
            spi: Schedule Performance Index
        
        Returns:
            Risk level string (CRITICAL, HIGH, MEDIUM, LOW)
        """
        critical_flags = 0
        high_flags = 0
        medium_flags = 0
        
        # Budget utilization checks
        if budget_utilization > 100:
            critical_flags += 1
        elif budget_utilization > 90:
            high_flags += 1
        elif budget_utilization > 80:
            medium_flags += 1
        
        # Profit margin checks
        if profit_margin < 0:
            critical_flags += 1
        elif profit_margin < 5:
            high_flags += 1
        elif profit_margin < 10:
            medium_flags += 1
        
        # CPI checks (cost performance)
        if cpi < Decimal('0.8'):
            critical_flags += 1
        elif cpi < Decimal('0.9'):
            high_flags += 1
        elif cpi < Decimal('0.95'):
            medium_flags += 1
        
        # SPI checks (schedule performance)
        if spi < Decimal('0.8'):
            critical_flags += 1
        elif spi < Decimal('0.9'):
            high_flags += 1
        elif spi < Decimal('0.95'):
            medium_flags += 1
        
        # Determine overall risk level
        if critical_flags >= 2 or (critical_flags >= 1 and high_flags >= 2):
            return 'CRITICAL'
        elif critical_flags >= 1 or high_flags >= 2:
            return 'HIGH'
        elif high_flags >= 1 or medium_flags >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    @staticmethod
    def _determine_project_health(
        risk_level: str,
        budget_utilization: Decimal,
        profit_margin: Decimal,
        is_behind_schedule: bool
    ) -> str:
        """
        Determine overall project health status
        
        Health Levels:
            - EXCELLENT: All metrics in great shape
            - GOOD: On track, minor issues
            - WARNING: Some concerns
            - CRITICAL: Serious issues
        
        Returns:
            Health status string
        """
        if risk_level == 'CRITICAL':
            return 'CRITICAL'
        elif risk_level == 'HIGH':
            return 'WARNING'
        elif risk_level == 'MEDIUM':
            if budget_utilization < 70 and profit_margin > 15:
                return 'GOOD'
            else:
                return 'WARNING'
        else:  # LOW risk
            if budget_utilization < 60 and profit_margin > 20 and not is_behind_schedule:
                return 'EXCELLENT'
            else:
                return 'GOOD'
    
    @staticmethod
    def compute_portfolio_summary() -> Dict[str, Any]:
        """
        Compute portfolio-wide summary statistics
        
        Returns:
            Dictionary with portfolio metrics including:
                - active_projects: Count of active projects
                - total_contract_value: Sum of all project values
                - total_expenses: Sum of all approved expenses
                - total_revenue: Sum of all client payments
                - total_profit: Revenue - Expenses
                - projects_over_budget: Count of projects exceeding budget
                - projects_behind_schedule: Count of delayed projects
                - avg_budget_utilization: Average budget utilization
                - avg_profit_margin: Average profit margin
                - high_risk_projects: Count of high/critical risk projects
        """
        # Active projects (not CANCELLED or COMPLETED)
        active_projects = Project.objects.exclude(
            status__in=['CANCELLED', 'COMPLETED']
        )
        
        # Count active projects
        active_projects_count = active_projects.count()
        
        # Total contract value across all active projects
        total_contract_value = active_projects.aggregate(
            total=Sum('project_value')
        )['total'] or Decimal('0.00')
        
        # Total expenses across all projects
        total_expenses = Expense.objects.filter(
            project__in=active_projects,
            approval_status='APPROVED'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Total revenue across all projects
        total_revenue = ClientPayment.objects.filter(
            project__in=active_projects
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Total profit
        total_profit = total_revenue - total_expenses
        
        # Projects over budget
        projects_over_budget_count = ProjectMetrics.objects.filter(
            project__in=active_projects,
            is_over_budget=True
        ).count()
        
        # Projects behind schedule
        projects_behind_schedule_count = ProjectMetrics.objects.filter(
            project__in=active_projects,
            is_behind_schedule=True
        ).count()
        
        # High risk projects
        high_risk_count = ProjectMetrics.objects.filter(
            project__in=active_projects,
            risk_level__in=['HIGH', 'CRITICAL']
        ).count()
        
        # Average budget utilization
        avg_budget_utilization = ProjectMetrics.objects.filter(
            project__in=active_projects
        ).aggregate(avg=Sum('budget_utilization'))['avg'] or Decimal('0.00')
        
        if active_projects_count > 0:
            avg_budget_utilization = avg_budget_utilization / active_projects_count
        
        # Average profit margin
        avg_profit_margin = ProjectMetrics.objects.filter(
            project__in=active_projects
        ).aggregate(avg=Sum('profit_margin'))['avg'] or Decimal('0.00')
        
        if active_projects_count > 0:
            avg_profit_margin = avg_profit_margin / active_projects_count
        
        return {
            'active_projects': active_projects_count,
            'total_contract_value': total_contract_value,
            'total_expenses': total_expenses,
            'total_revenue': total_revenue,
            'total_profit': total_profit,
            'projects_over_budget': projects_over_budget_count,
            'projects_behind_schedule': projects_behind_schedule_count,
            'high_risk_projects': high_risk_count,
            'avg_budget_utilization': avg_budget_utilization,
            'avg_profit_margin': avg_profit_margin,
        }
    
    @staticmethod
    @transaction.atomic
    def update_all_project_metrics() -> int:
        """
        Update metrics for all active projects
        
        Returns:
            Number of projects updated
        """
        # Get all active projects
        active_projects = Project.objects.exclude(
            status__in=['CANCELLED']
        )
        
        updated_count = 0
        for project in active_projects:
            PortfolioAnalyticsService.compute_project_risk_indicators(str(project.id))
            updated_count += 1
        
        return updated_count
