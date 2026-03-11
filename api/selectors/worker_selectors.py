"""
Worker Selectors - Optimized queries for worker analytics
"""
from django.db.models import Sum, Count, Q, F, DecimalField
from django.db.models.functions import Coalesce
from apps.workers.models import Worker, DailyLabourRecord


def get_workers_unpaid_wages():
    """
    Get all workers with unpaid wages
    """
    workers = Worker.objects.prefetch_related(
        'dailylabourrecord_set'
    ).annotate(
        total_days_worked=Count('dailylabourrecord'),
        days_unpaid=Count('dailylabourrecord', filter=Q(dailylabourrecord__paid=False)),
        total_unpaid_wages=Coalesce(
            Sum('dailylabourrecord__daily_wage', filter=Q(dailylabourrecord__paid=False)),
            0,
            output_field=DecimalField()
        )
    ).filter(
        total_unpaid_wages__gt=0
    ).order_by('-total_unpaid_wages')
    
    return workers
