"""
Worker Analytics Services - Business logic for worker analytics
"""
from decimal import Decimal


def calculate_unpaid_wages(workers):
    """
    Calculate unpaid wages for workers
    
    Returns:
        list: Workers with unpaid wages
    """
    unpaid_data = []
    
    for worker in workers:
        total_unpaid = worker.total_unpaid_wages or Decimal('0')
        
        if total_unpaid > 0:
            unpaid_data.append({
                'worker_id': str(worker.id),
                'worker_name': worker.name,
                'worker_role': worker.role,
                'id_number': worker.id_number,
                'phone': worker.phone,
                'total_days_worked': worker.total_days_worked or 0,
                'days_unpaid': worker.days_unpaid or 0,
                'total_unpaid_wages': float(total_unpaid),
            })
    
    return unpaid_data
