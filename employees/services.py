import csv
from django.http import HttpResponse
from django.db.models import Q
from .models import Employee


def filter_employees(queryset, get_params):
    """
    Applies search, multi-field filters, and sorting to the Employee queryset.
    """
    search_query = get_params.get('q', '').strip()
    department_id = get_params.get('department', '').strip()
    status = get_params.get('status', '').strip()
    employment_type = get_params.get('employment_type', '').strip()
    sort_by = get_params.get('sort', '-created_at').strip()

    if search_query:
        queryset = queryset.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(designation__icontains=search_query)
        )

    if department_id and department_id.isdigit():
        queryset = queryset.filter(department_id=department_id)

    if status:
        queryset = queryset.filter(status=status)

    if employment_type:
        queryset = queryset.filter(employment_type=employment_type)

    valid_sort_fields = [
        'created_at', '-created_at',
        'first_name', '-first_name',
        'salary', '-salary',
        'date_of_joining', '-date_of_joining',
        'employee_id', '-employee_id',
    ]
    if sort_by in valid_sort_fields:
        queryset = queryset.order_by(sort_by)
    else:
        queryset = queryset.order_by('-created_at')

    return queryset


def generate_employees_csv(queryset):
    """
    Constructs an HTTP response streaming a CSV of the filtered employees.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Employee ID', 'First Name', 'Last Name', 'Email', 'Phone',
        'Gender', 'Department', 'Designation', 'Employment Type',
        'Status', 'Date of Joining', 'Salary', 'Address'
    ])

    for emp in queryset.select_related('department'):
        writer.writerow([
            emp.employee_id,
            emp.first_name,
            emp.last_name,
            emp.email,
            emp.phone,
            emp.gender,
            emp.department.name if emp.department else 'N/A',
            emp.designation,
            emp.employment_type,
            emp.status,
            emp.date_of_joining.strftime('%Y-%m-%d') if emp.date_of_joining else '',
            f"{emp.salary:.2f}",
            emp.address.replace('\n', ' ') if emp.address else ''
        ])

    return response

