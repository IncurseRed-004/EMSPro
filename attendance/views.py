from datetime import date, datetime, time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from core.decorators import role_required, verify_employee_ownership
from employees.models import Employee
from departments.models import Department
from .models import Attendance
from .forms import AttendanceForm
from .services import filter_attendance, get_employee_monthly_summary


@login_required
@role_required('Admin', 'HR Manager')
def attendance_list(request):
    """
    HR/Admin view: Search, filter, and review attendance records by date, employee, and status.
    """
    attendance_qs = Attendance.objects.select_related('employee', 'employee__department').all()
    filtered_qs = filter_attendance(attendance_qs, request.GET)

    paginator = Paginator(filtered_qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    employees = Employee.objects.filter(status='Active').order_by('first_name')
    departments = Department.objects.all().order_by('name')

    return render(request, 'attendance/list.html', {
        'page_obj': page_obj,
        'employees': employees,
        'departments': departments,
        'total_count': filtered_qs.count(),
        'current_date': request.GET.get('date', ''),
        'selected_employee': request.GET.get('employee', ''),
        'selected_dept': request.GET.get('department', ''),
        'selected_status': request.GET.get('status', ''),
    })


@login_required
@role_required('Admin', 'HR Manager')
def attendance_create(request):
    """
    Allows HR/Admin to manually log or adjust attendance for an employee.
    """
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            att = form.save()
            messages.success(request, f"Attendance record for {att.employee.full_name} on {att.date} saved.")
            return redirect('attendance:list')
        else:
            messages.error(request, "Failed to save attendance. Review the errors below.")
    else:
        initial = {'date': date.today(), 'status': 'Present'}
        form = AttendanceForm(initial=initial)

    return render(request, 'attendance/form.html', {
        'form': form,
        'title': 'Log Attendance Record',
        'is_edit': False,
    })


@login_required
@role_required('Admin', 'HR Manager')
def attendance_update(request, pk):
    """
    Updates an existing attendance entry.
    """
    record = get_object_or_404(Attendance.objects.select_related('employee'), pk=pk)

    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, f"Attendance record for {record.employee.full_name} updated.")
            return redirect('attendance:list')
        else:
            messages.error(request, "Failed to update attendance record.")
    else:
        form = AttendanceForm(instance=record)

    return render(request, 'attendance/form.html', {
        'form': form,
        'record': record,
        'title': f'Edit Attendance: {record.employee.full_name} ({record.date})',
        'is_edit': True,
    })


@login_required
@role_required('Admin', 'HR Manager')
@require_POST
def attendance_delete(request, pk):
    """
    Deletes an attendance record.
    """
    record = get_object_or_404(Attendance, pk=pk)
    emp_name = record.employee.full_name
    rec_date = record.date
    record.delete()
    messages.success(request, f"Attendance record for {emp_name} on {rec_date} has been removed.")
    return redirect('attendance:list')


@login_required
@require_POST
def check_in(request):
    """
    One-click attendance check-in for the logged-in employee.
    """
    employee = getattr(request.user, 'employee_profile', None)
    if not employee:
        messages.error(request, "Only registered employees can check in.")
        return redirect('dashboard:home')

    today = date.today()
    att, created = Attendance.objects.get_or_create(
        employee=employee,
        date=today,
        defaults={'status': 'Present'}
    )

    if att.check_in:
        messages.warning(request, f"You have already checked in today at {att.check_in.strftime('%I:%M %p')}.")
    else:
        now_time = timezone.localtime().time()
        att.check_in = now_time
        # Check if late (after 09:30 AM)
        if now_time > time(9, 30):
            att.status = 'Late'
        else:
            att.status = 'Present'
        att.save()
        messages.success(request, f"Checked in successfully at {now_time.strftime('%I:%M %p')}!")

    return redirect('dashboard:home')


@login_required
@require_POST
def check_out(request):
    """
    One-click attendance check-out for the logged-in employee.
    """
    employee = getattr(request.user, 'employee_profile', None)
    if not employee:
        messages.error(request, "Only registered employees can check out.")
        return redirect('dashboard:home')

    today = date.today()
    try:
        att = Attendance.objects.get(employee=employee, date=today)
    except Attendance.DoesNotExist:
        messages.error(request, "You must check in before checking out.")
        return redirect('dashboard:home')

    if att.check_out:
        messages.warning(request, f"You have already checked out today at {att.check_out.strftime('%I:%M %p')}.")
    else:
        now_time = timezone.localtime().time()
        att.check_out = now_time
        # If total work duration is less than 4 hours, mark as Half-day
        if att.duration_hours and att.duration_hours < 4.0:
            att.status = 'Half-day'
        att.save()
        messages.success(request, f"Checked out successfully at {now_time.strftime('%I:%M %p')}!")

    return redirect('dashboard:home')


@login_required
def monthly_summary(request, employee_id):
    """
    Renders monthly summary breakdown and calendar view for an employee.
    """
    employee = get_object_or_404(Employee.objects.select_related('department'), pk=employee_id)
    verify_employee_ownership(request, employee)

    today = date.today()
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except (ValueError, TypeError):
        year = today.year
        month = today.month

    summary = get_employee_monthly_summary(employee, year=year, month=month)

    # Previous and next month helpers
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    return render(request, 'attendance/monthly_summary.html', {
        'employee': employee,
        'summary': summary,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    })
