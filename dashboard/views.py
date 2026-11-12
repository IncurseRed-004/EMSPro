from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from employees.models import Employee
from departments.models import Department
from attendance.models import Attendance
from leaves.models import LeaveRequest
from leaves.services import calculate_leave_balance


@login_required
def dashboard_home(request):
    """
    Role-aware dashboard view:
    - Renders the executive analytics dashboard for Admin and HR Managers.
    - Renders the self-service personal workspace for Employees.
    """
    user = request.user
    user_groups = set(user.groups.values_list('name', flat=True))
    is_admin_or_hr = user.is_superuser or ('Admin' in user_groups) or ('HR Manager' in user_groups)

    today = date.today()

    if is_admin_or_hr:
        # --- Executive Metrics ---
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(status='Active').count()
        total_departments = Department.objects.count()
        pending_leaves = LeaveRequest.objects.filter(status='Pending').count()
        present_today = Attendance.objects.filter(
            date=today,
            status__in=['Present', 'Late', 'Half-day']
        ).count()

        # 1. Chart Data: Employees by Department (Doughnut)
        dept_data = Department.objects.annotate(emp_count=Count('employees')).order_by('-emp_count')
        dept_chart = {
            'labels': [d.name for d in dept_data],
            'data': [d.emp_count for d in dept_data],
        }

        # 2. Chart Data: Employment Type Split (Bar)
        type_counts = Employee.objects.values('employment_type').annotate(count=Count('id'))
        emp_type_dict = {item['employment_type']: item['count'] for item in type_counts}
        all_types = ['Full-time', 'Part-time', 'Contract', 'Intern']
        emp_type_chart = {
            'labels': all_types,
            'data': [emp_type_dict.get(t, 0) for t in all_types],
        }

        # 3. Chart Data: Attendance Trend (Last 14 days line chart)
        attendance_labels = []
        attendance_counts = []
        for i in range(13, -1, -1):
            day = today - timedelta(days=i)
            # format as Mon 01/15
            attendance_labels.append(day.strftime('%b %d'))
            count = Attendance.objects.filter(
                date=day,
                status__in=['Present', 'Late', 'Half-day']
            ).count()
            attendance_counts.append(count)

        attendance_chart = {
            'labels': attendance_labels,
            'data': attendance_counts,
        }

        # Recent joiners & pending leaves
        recent_employees = Employee.objects.select_related('department').order_by('-date_of_joining')[:5]
        pending_leave_requests = LeaveRequest.objects.select_related(
            'employee', 'employee__department'
        ).filter(status='Pending').order_by('applied_on')[:5]

        context = {
            'is_admin_or_hr': True,
            'total_employees': total_employees,
            'active_employees': active_employees,
            'total_departments': total_departments,
            'pending_leaves': pending_leaves,
            'present_today': present_today,
            'recent_employees': recent_employees,
            'pending_leave_requests': pending_leave_requests,
            'dept_chart': dept_chart,
            'emp_type_chart': emp_type_chart,
            'attendance_chart': attendance_chart,
        }
        return render(request, 'dashboard/admin_dashboard.html', context)

    else:
        # --- Employee Self-Service Workspace ---
        employee = getattr(user, 'employee_profile', None)
        if not employee:
            return render(request, 'dashboard/no_profile.html')

        # Today's attendance record
        today_attendance = Attendance.objects.filter(employee=employee, date=today).first()

        # Leave balances
        leave_balances = calculate_leave_balance(employee)

        # Recent personal records
        recent_attendance = Attendance.objects.filter(employee=employee).order_by('-date')[:7]
        recent_leaves = LeaveRequest.objects.filter(employee=employee).order_by('-applied_on')[:5]

        # Monthly summary current month
        month_present = Attendance.objects.filter(
            employee=employee,
            date__year=today.year,
            date__month=today.month,
            status__in=['Present', 'Late', 'Half-day']
        ).count()

        context = {
            'is_admin_or_hr': False,
            'employee': employee,
            'today_attendance': today_attendance,
            'leave_balances': leave_balances,
            'recent_attendance': recent_attendance,
            'recent_leaves': recent_leaves,
            'month_present': month_present,
            'today': today,
        }
        return render(request, 'dashboard/employee_dashboard.html', context)
