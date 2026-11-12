from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from core.decorators import role_required, verify_employee_ownership
from employees.models import Employee
from .models import LeaveRequest
from .forms import LeaveApplyForm, LeaveReviewForm
from .services import calculate_leave_balance


@login_required
def leave_list(request):
    """
    Displays leave requests:
    - Admin/HR see all requests across the organization with filters.
    - Employees see only their personal leave history and current balances.
    """
    user = request.user
    user_groups = set(user.groups.values_list('name', flat=True))
    is_admin_or_hr = user.is_superuser or ('Admin' in user_groups) or ('HR Manager' in user_groups)

    status_filter = request.GET.get('status', '').strip()
    type_filter = request.GET.get('type', '').strip()

    if is_admin_or_hr:
        leaves_qs = LeaveRequest.objects.select_related('employee', 'employee__department', 'reviewed_by').all()
        emp_filter = request.GET.get('employee', '').strip()
        if emp_filter and emp_filter.isdigit():
            leaves_qs = leaves_qs.filter(employee_id=emp_filter)
        balances = None
    else:
        employee = getattr(user, 'employee_profile', None)
        if not employee:
            messages.warning(request, "No employee profile found for your account.")
            return redirect('dashboard:home')
        leaves_qs = LeaveRequest.objects.filter(employee=employee).select_related('reviewed_by')
        balances = calculate_leave_balance(employee)

    if status_filter:
        leaves_qs = leaves_qs.filter(status=status_filter)
    if type_filter:
        leaves_qs = leaves_qs.filter(leave_type=type_filter)

    paginator = Paginator(leaves_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_employees = Employee.objects.filter(status='Active').order_by('first_name') if is_admin_or_hr else None

    return render(request, 'leaves/list.html', {
        'page_obj': page_obj,
        'balances': balances,
        'is_admin_or_hr': is_admin_or_hr,
        'all_employees': all_employees,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'selected_employee': request.GET.get('employee', ''),
    })


@login_required
def leave_apply(request):
    """
    Enables employees to apply for new leave.
    """
    employee = getattr(request.user, 'employee_profile', None)
    if not employee:
        messages.error(request, "Only registered employees can submit leave applications.")
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = LeaveApplyForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.status = 'Pending'
            try:
                leave.full_clean()
                leave.save()
                messages.success(request, f"Leave application submitted for {leave.duration_days} day(s)!")
                return redirect('leaves:list')
            except Exception as e:
                form.add_error(None, str(e))
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = LeaveApplyForm()

    balances = calculate_leave_balance(employee)

    return render(request, 'leaves/apply.html', {
        'form': form,
        'balances': balances,
        'employee': employee,
    })


@login_required
def leave_detail(request, pk):
    """
    Displays the details of a single leave request.
    """
    leave = get_object_or_404(
        LeaveRequest.objects.select_related('employee', 'employee__department', 'reviewed_by'),
        pk=pk
    )
    verify_employee_ownership(request, leave.employee)

    user_groups = set(request.user.groups.values_list('name', flat=True))
    can_review = request.user.is_superuser or ('Admin' in user_groups) or ('HR Manager' in user_groups)

    return render(request, 'leaves/detail.html', {
        'leave': leave,
        'can_review': can_review,
        'review_form': LeaveReviewForm(instance=leave) if can_review and leave.status == 'Pending' else None,
    })


@login_required
@role_required('Admin', 'HR Manager')
def leave_review(request, pk):
    """
    HR/Admin action to approve or reject a pending leave application with review remarks.
    """
    leave = get_object_or_404(
        LeaveRequest.objects.select_related('employee'),
        pk=pk
    )

    if request.method == 'POST':
        form = LeaveReviewForm(request.POST, instance=leave)
        if form.is_valid():
            reviewed_leave = form.save(commit=False)
            reviewed_leave.reviewed_by = request.user
            reviewed_leave.save()
            messages.success(request, f"Leave request marked as {reviewed_leave.status} successfully!")
            return redirect('leaves:list')
        else:
            messages.error(request, "Could not process review. Please check your input.")
    else:
        form = LeaveReviewForm(instance=leave)

    return render(request, 'leaves/review.html', {
        'leave': leave,
        'form': form,
    })


@login_required
@require_POST
def leave_cancel(request, pk):
    """
    Permits an employee to cancel their own pending leave request.
    """
    leave = get_object_or_404(LeaveRequest, pk=pk)

    # Ownership check
    if leave.employee.user != request.user and not request.user.is_superuser:
        raise PermissionDenied("You can only cancel your own leave requests.")

    if leave.status != 'Pending':
        messages.error(request, "Only pending leave requests can be cancelled.")
    else:
        leave.delete()
        messages.success(request, "Your leave application has been cancelled.")

    return redirect('leaves:list')
