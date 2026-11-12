from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """
    Decorator for views that checks whether a user has at least one of the
    specified roles ('Admin', 'HR Manager', 'Employee').
    Superusers automatically bypass this check.
    If the user does not have an allowed role, PermissionDenied is raised (triggering 403).
    """
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            # Superusers always have full access
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check user group memberships
            user_groups = set(user.groups.values_list('name', flat=True))
            allowed_set = set(allowed_roles)

            if user_groups.intersection(allowed_set):
                return view_func(request, *args, **kwargs)

            # Role not permitted
            raise PermissionDenied("You do not have the required permissions to access this page.")

        return _wrapped_view
    return decorator


def verify_employee_ownership(request, employee):
    """
    Helper to verify if the requesting user owns the employee record,
    or has Admin / HR privileges.
    Raises PermissionDenied if neither condition is met.
    """
    if request.user.is_superuser:
        return True

    user_groups = set(request.user.groups.values_list('name', flat=True))
    if 'Admin' in user_groups or 'HR Manager' in user_groups:
        return True

    # Employee checking own record
    if employee.user == request.user:
        return True

    raise PermissionDenied("You are not authorized to view or edit another employee's record.")

