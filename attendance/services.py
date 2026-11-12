import calendar
from datetime import date
from django.db.models import Q
from .models import Attendance


def filter_attendance(queryset, get_params):
    """
    Applies filters to Attendance records by date, employee, department, and status.
    """
    date_filter = get_params.get('date', '').strip()
    employee_id = get_params.get('employee', '').strip()
    dept_id = get_params.get('department', '').strip()
    status = get_params.get('status', '').strip()
    month_str = get_params.get('month', '').strip()  # format: YYYY-MM

    if date_filter:
        queryset = queryset.filter(date=date_filter)

    if employee_id and employee_id.isdigit():
        queryset = queryset.filter(employee_id=employee_id)

    if dept_id and dept_id.isdigit():
        queryset = queryset.filter(employee__department_id=dept_id)

    if status:
        queryset = queryset.filter(status=status)

    if month_str and '-' in month_str:
        try:
            year, month = map(int, month_str.split('-'))
            queryset = queryset.filter(date__year=year, date__month=month)
        except ValueError:
            pass

    return queryset.order_by('-date', '-check_in')


def get_employee_monthly_summary(employee, year=None, month=None):
    """
    Generates structured attendance summary statistics and day-by-day logs
    for a given employee in a specific month.
    """
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    records = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    ).order_by('date')

    status_counts = {
        'Present': 0,
        'Late': 0,
        'Half_day': 0,
        'Absent': 0,
    }

    total_work_hours = 0.0

    for rec in records:
        key = 'Half_day' if rec.status == 'Half-day' else rec.status
        if key in status_counts:
            status_counts[key] += 1
        hrs = rec.duration_hours
        if hrs:
            total_work_hours += hrs

    num_days = calendar.monthrange(year, month)[1]
    month_name = calendar.month_name[month]

    return {
        'year': year,
        'month': month,
        'month_name': month_name,
        'num_days': num_days,
        'records': records,
        'status_counts': status_counts,
        'total_work_hours': round(total_work_hours, 1),
        'attendance_rate': round((status_counts['Present'] + status_counts['Late'] + status_counts['Half_day']) / max(1, len(records)) * 100, 1) if records else 0,
    }

