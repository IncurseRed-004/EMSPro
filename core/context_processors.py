def role_context(request):
    """
    Exposes role flags and current employee profile to all templates.
    """
    if not request.user.is_authenticated:
        return {
            'user_role': 'Anonymous',
            'is_admin': False,
            'is_hr': False,
            'is_admin_or_hr': False,
            'user_employee': None,
        }

    user = request.user
    user_groups = set(user.groups.values_list('name', flat=True))

    is_admin = user.is_superuser or ('Admin' in user_groups)
    is_hr = 'HR Manager' in user_groups
    is_admin_or_hr = is_admin or is_hr

    if is_admin:
        role = 'Admin'
    elif is_hr:
        role = 'HR Manager'
    elif 'Employee' in user_groups:
        role = 'Employee'
    else:
        role = 'Staff' if user.is_staff else 'User'

    user_employee = getattr(user, 'employee_profile', None)

    return {
        'user_role': role,
        'is_admin': is_admin,
        'is_hr': is_hr,
        'is_admin_or_hr': is_admin_or_hr,
        'user_employee': user_employee,
    }

