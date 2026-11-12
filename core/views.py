from django.shortcuts import render


def custom_permission_denied_view(request, exception=None):
    """Render custom 403 Forbidden page."""
    context = {
        'title': '403 - Access Denied',
        'exception': str(exception) if exception else 'You do not have permission to access this resource.'
    }
    return render(request, 'errors/403.html', context, status=403)


def custom_page_not_found_view(request, exception=None):
    """Render custom 404 Page Not Found page."""
    context = {
        'title': '404 - Page Not Found',
    }
    return render(request, 'errors/404.html', context, status=404)


def custom_server_error_view(request):
    """Render custom 500 Server Error page."""
    context = {
        'title': '500 - Internal Server Error',
    }
    return render(request, 'errors/500.html', context, status=500)

