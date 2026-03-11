from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from apps.projects.models import Project


class CashFlowForecast(models.Model):
    """
    Stores monthly cash flow forecasts for projects.
    
    Each record represents a single month's forecast for a specific project.
    Multiple records for different months create a time series forecast.
    """
    
    # Relationship
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='cash_flow_forecasts'
    )
    
    # Forecast Period
    forecast_month = models.DateField(
        help_text="First day of the forecast month (YYYY-MM-01)"
    )
    forecast_generated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this forecast was computed"
    )
    
    # === INFLOWS ===
    
    # Valuation-based inflows
    expected_valuations = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Expected IPC/valuation submissions"
    )
    
    expected_client_payments = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Expected client payments (approved valuations)"
    )
    
    expected_retention_releases = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Expected retention money releases"
    )
    
    expected_variation_order_payments = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Expected variation order payments"
    )
    
    # Total inflow (computed)
    total_inflow = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Sum of all expected inflows"
    )
    
    # === OUTFLOWS ===
    
    expected_supplier_payments = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Expected supplier invoice payments"
    )
    
    expected_labour_costs = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Expected labour/payroll costs"
    )
    
    expected_consultant_fees = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Expected consultant/professional fees"
    )
    
    expected_procurement_payments = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Expected procurement-related payments"
    )
    
    expected_site_expenses = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Expected site operational expenses"
    )
    
    expected_other_expenses = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Other expected expenses"
    )
    
    # Total outflow (computed)
    total_outflow = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Sum of all expected outflows"
    )
    
    # === CALCULATED METRICS ===
    
    net_cash_flow = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Net cash flow (inflow - outflow)"
    )
    
    cumulative_cash_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Cumulative project cash balance up to this month"
    )
    
    # Forecast Quality Indicator
    class ConfidenceLevel(models.TextChoices):
        LOW = 'LOW', 'Low Confidence'
        MEDIUM = 'MEDIUM', 'Medium Confidence'
        HIGH = 'HIGH', 'High Confidence'
    
    confidence_level = models.CharField(
        max_length=10,
        choices=ConfidenceLevel.choices,
        default=ConfidenceLevel.MEDIUM,
        help_text="Forecast reliability based on project progress, historical data, and variance"
    )
    
    # Metadata
    is_actual = models.BooleanField(
        default=False,
        help_text="True if this month has actual data (not forecast)"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cashflow_forecast'
        ordering = ['project', 'forecast_month']
        unique_together = [['project', 'forecast_month']]
        indexes = [
            models.Index(fields=['project', 'forecast_month']),
            models.Index(fields=['forecast_month']),
            models.Index(fields=['is_actual']),
        ]
        verbose_name = 'Cash Flow Forecast'
        verbose_name_plural = 'Cash Flow Forecasts'
    
    def __str__(self):
        return f"{self.project.name} - {self.forecast_month.strftime('%Y-%m')}"
    
    def save(self, *args, **kwargs):
        """Auto-compute totals before saving"""
        # Compute total inflow
        self.total_inflow = (
            self.expected_valuations +
            self.expected_client_payments +
            self.expected_retention_releases +
            self.expected_variation_order_payments
        )
        
        # Compute total outflow
        self.total_outflow = (
            self.expected_supplier_payments +
            self.expected_labour_costs +
            self.expected_consultant_fees +
            self.expected_procurement_payments +
            self.expected_site_expenses +
            self.expected_other_expenses
        )
        
        # Compute net cash flow
        self.net_cash_flow = self.total_inflow - self.total_outflow
        
        super().save(*args, **kwargs)


class PortfolioCashFlowSummary(models.Model):
    """
    Portfolio-wide cash flow summary for a given forecast month.
    
    Aggregates cash flow across all active projects.
    """
    
    forecast_month = models.DateField(
        unique=True,
        help_text="First day of the forecast month (YYYY-MM-01)"
    )
    
    # Portfolio aggregates
    total_portfolio_inflow = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    total_portfolio_outflow = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    net_portfolio_cash_flow = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    cumulative_portfolio_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Cumulative portfolio cash balance"
    )
    
    # Project counts
    active_projects_count = models.IntegerField(default=0)
    projects_with_negative_flow = models.IntegerField(default=0)
    
    # Liquidity Metrics
    average_cash_burn_rate = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Average monthly cash outflow across portfolio (burn rate)"
    )
    
    cash_runway_months = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0'),
        help_text="Estimated months of operation with current cash balance (balance / burn_rate)"
    )
    
    # Metadata
    forecast_generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'portfolio_cashflow_summary'
        ordering = ['forecast_month']
        verbose_name = 'Portfolio Cash Flow Summary'
        verbose_name_plural = 'Portfolio Cash Flow Summaries'
    
    def __str__(self):
        return f"Portfolio Cash Flow - {self.forecast_month.strftime('%Y-%m')}"
