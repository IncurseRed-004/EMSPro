from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from core.decorators import role_required, verify_employee_ownership
from departments.models import Department
from .models import Employee
from .forms import EmployeeCreateForm, EmployeeUpdateForm
from .services import filter_employees, generate_employees_csv


@login_required
@role_required('Admin', 'HR Manager')
def employee_list(request):
    """
    Lists employees with multi-field search, filters, sorting, and pagination.
    Supports toggling between table and card/grid view via query param 'view'.
    """
    employees_qs = Employee.objects.select_related('department', 'user').all()
    filtered_qs = filter_employees(employees_qs, request.GET)

    paginator = Paginator(filtered_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.all().order_by('name')
    view_mode = request.GET.get('view', 'table')  # 'table' or 'grid'

    return render(request, 'employees/list.html', {
        'page_obj': page_obj,
        'departments': departments,
        'view_mode': view_mode,
        'total_count': filtered_qs.count(),
        'current_params': request.GET.urlencode(),
    })


@login_required
def employee_detail(request, pk):
    """
    Displays full details for a single employee record.
    Enforces ownership permissions: standard employees may only inspect their own profile.
    """
    employee = get_object_or_404(
        Employee.objects.select_related('department', 'user'),
        pk=pk
    )
    verify_employee_ownership(request, employee)

    # Fetch recent attendance and leave requests for display
    recent_attendance = employee.attendances.order_by('-date')[:7]
    recent_leaves = employee.leave_requests.order_by('-applied_on')[:5]

    return render(request, 'employees/detail.html', {
        'employee': employee,
        'recent_attendance': recent_attendance,
        'recent_leaves': recent_leaves,
    })


@login_required
@role_required('Admin', 'HR Manager')
def employee_create(request):
    """
    Creates a new employee record and linked User account.
    """
    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST, request.FILES)
        if form.is_valid():
            emp = form.save()
            messages.success(request, f'Employee "{emp.full_name}" ({emp.employee_id}) created successfully!')
            return redirect('employees:detail', pk=emp.pk)
        else:
            messages.error(request, "Failed to create employee. Please review the errors below.")
    else:
        form = EmployeeCreateForm()

    return render(request, 'employees/form.html', {
        'form': form,
        'title': 'Add New Employee',
        'is_edit': False,
    })


@login_required
@role_required('Admin', 'HR Manager')
def employee_update(request, pk):
    """
    Updates an employee's professional and profile details.
    """
    employee = get_object_or_404(Employee.objects.select_related('user'), pk=pk)

    if request.method == 'POST':
        form = EmployeeUpdateForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            emp = form.save()
            messages.success(request, f'Employee record for "{emp.full_name}" updated successfully!')
            return redirect('employees:detail', pk=emp.pk)
        else:
            messages.error(request, "Failed to update employee. Please check the errors below.")
    else:
        form = EmployeeUpdateForm(instance=employee)

    return render(request, 'employees/form.html', {
        'form': form,
        'employee': employee,
        'title': f'Edit Employee: {employee.full_name}',
        'is_edit': True,
    })


@login_required
@role_required('Admin', 'HR Manager')
@require_POST
def employee_delete(request, pk):
    """
    Hard-deletes an employee and associated user account upon modal confirmation.
    """
    employee = get_object_or_404(Employee, pk=pk)
    user = employee.user
    name = employee.full_name
    employee.delete()
    if user:
        user.delete()
    messages.success(request, f'Employee "{name}" has been permanently removed.')
    return redirect('employees:list')


@login_required
@role_required('Admin', 'HR Manager')
@require_POST
def employee_deactivate(request, pk):
    """
    Soft-deletes/deactivates an employee by setting status to Terminated.
    """
    employee = get_object_or_404(Employee, pk=pk)
    employee.status = 'Terminated'
    employee.save()
    if employee.user:
        employee.user.is_active = False
        employee.user.save()
    messages.warning(request, f'Employee "{employee.full_name}" has been deactivated (status set to Terminated).')
    return redirect('employees:detail', pk=employee.pk)


@login_required
@role_required('Admin', 'HR Manager')
def employee_export_csv(request):
    """
    Exports filtered list of employees to CSV.
    """
    employees_qs = Employee.objects.select_related('department').all()
    filtered_qs = filter_employees(employees_qs, request.GET)
    return generate_employees_csv(filtered_qs)
