from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.core.paginator import Paginator
from core.decorators import role_required
from .models import Department
from .forms import DepartmentForm


@login_required
@role_required('Admin', 'HR Manager')
def department_list(request):
    """
    Lists departments with employee count annotations, search, and pagination.
    """
    search_query = request.GET.get('q', '').strip()
    departments_qs = Department.objects.annotate(
        total_employees=Count('employees')
    ).select_related('head')

    if search_query:
        departments_qs = departments_qs.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    sort = request.GET.get('sort', 'name')
    if sort in ['name', '-name', 'total_employees', '-total_employees', 'created_at', '-created_at']:
        departments_qs = departments_qs.order_by(sort)

    paginator = Paginator(departments_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'departments/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort': sort,
        'total_count': departments_qs.count(),
    })


@login_required
@role_required('Admin', 'HR Manager')
def department_detail(request, pk):
    """
    Displays department details, leadership, and its team members.
    """
    department = get_object_or_404(
        Department.objects.annotate(total_employees=Count('employees')).select_related('head'),
        pk=pk
    )
    employees = department.employees.select_related('user').order_by('first_name')

    return render(request, 'departments/detail.html', {
        'department': department,
        'employees': employees,
    })


@login_required
@role_required('Admin', 'HR Manager')
def department_create(request):
    """
    Creates a new department.
    """
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f'Department "{dept.name}" created successfully!')
            return redirect('departments:detail', pk=dept.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm()

    return render(request, 'departments/form.html', {
        'form': form,
        'title': 'Create Department',
        'is_edit': False,
    })


@login_required
@role_required('Admin', 'HR Manager')
def department_update(request, pk):
    """
    Updates an existing department.
    """
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f'Department "{dept.name}" updated successfully!')
            return redirect('departments:detail', pk=dept.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm(instance=department)

    return render(request, 'departments/form.html', {
        'form': form,
        'department': department,
        'title': f'Edit Department: {department.name}',
        'is_edit': True,
    })


@login_required
@role_required('Admin', 'HR Manager')
@require_POST
def department_delete(request, pk):
    """
    Deletes a department after confirmation modal submission.
    """
    department = get_object_or_404(Department, pk=pk)
    name = department.name
    department.delete()
    messages.success(request, f'Department "{name}" has been deleted.')
    return redirect('departments:list')
