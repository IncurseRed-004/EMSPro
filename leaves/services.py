from datetime import date
from django.db.models import Sum
from .models import LeaveRequest

ANNUAL_LEAVE_QUOTAS = {
    'Casual': 12,
    'Sick': 10,
    'Paid': 15,
}


def calculate_leave_balance(employee, target_year=None):
    """
    Computes leave quotas, approved usage, and remaining days for an employee.
    """
    if target_year is None:
        target_year = date.today().year

    approved_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='Approved',
        start_date__year=target_year
    )

    balances = {}
    for leave_type, total_quota in ANNUAL_LEAVE_QUOTAS.items():
        type_leaves = approved_leaves.filter(leave_type=leave_type)
        used_days = sum(l.duration_days for l in type_leaves)
        remaining = max(0, total_quota - used_days)
        balances[leave_type] = {
            'quota': total_quota,
            'used': used_days,
            'remaining': remaining,
        }

    # Unpaid leaves are tracked without quota limits
    unpaid_leaves = approved_leaves.filter(leave_type='Unpaid')
    balances['Unpaid'] = {
        'quota': 'Flexible',
        'used': sum(l.duration_days for l in unpaid_leaves),
        'remaining': 'Flexible',
    }

    return balances

