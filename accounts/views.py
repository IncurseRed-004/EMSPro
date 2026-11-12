from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import LoginForm, UserProfileUpdateForm
from employees.models import Employee


def user_login(request):
    """
    Function-based view for user authentication.
    Redirects authenticated users directly to their dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:home')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """
    Logs out the current user and redirects to login with confirmation.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')


@login_required
def user_profile(request):
    """
    Displays personal profile and allows editing contact info and photo.
    """
    employee = getattr(request.user, 'employee_profile', None)

    if request.method == 'POST':
        if employee:
            form = UserProfileUpdateForm(request.POST, request.FILES, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, "Your profile has been updated successfully.")
                return redirect('accounts:profile')
        else:
            # Fallback for superuser with no attached Employee instance
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            request.user.email = request.POST.get('email', request.user.email)
            request.user.save()
            messages.success(request, "User details updated successfully.")
            return redirect('accounts:profile')
    else:
        form = UserProfileUpdateForm(instance=employee) if employee else None

    return render(request, 'accounts/profile.html', {
        'employee': employee,
        'form': form,
    })


@login_required
def change_password(request):
    """
    Allows authenticated users to change their password securely.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep session active
            messages.success(request, "Your password was successfully updated!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
