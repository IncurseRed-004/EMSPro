from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from .models import Employee
from departments.models import Department


class EmployeeCreateForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. john.doe'})
    )
    password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Initial password for login'})
    )
    role = forms.ChoiceField(
        choices=[('Employee', 'Employee'), ('HR Manager', 'HR Manager')],
        initial='Employee',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'gender',
            'date_of_birth', 'address', 'photo', 'department',
            'designation', 'date_of_joining', 'salary',
            'employment_type', 'status'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'work.email@company.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 555-0199'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Full residential address'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Software Engineer'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 75000.00', 'step': '0.01'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists() or Employee.objects.filter(email=email).exists():
            raise ValidationError('A user or employee with this email already exists.')
        return email

    def save(self, commit=True):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        email = self.cleaned_data['email']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        role_name = self.cleaned_data['role']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        group, _ = Group.objects.get_or_create(name=role_name)
        user.groups.add(group)

        employee = super().save(commit=False)
        employee.user = user

        if commit:
            employee.save()
        return employee


class EmployeeUpdateForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[('Employee', 'Employee'), ('HR Manager', 'HR Manager')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'gender',
            'date_of_birth', 'address', 'photo', 'department',
            'designation', 'date_of_joining', 'salary',
            'employment_type', 'status'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            user = self.instance.user
            if user.groups.filter(name='HR Manager').exists():
                self.fields['role'].initial = 'HR Manager'
            else:
                self.fields['role'].initial = 'Employee'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        emp_qs = Employee.objects.filter(email=email).exclude(pk=self.instance.pk)
        if emp_qs.exists():
            raise ValidationError('An employee with this email already exists.')
        user_qs = User.objects.filter(email=email).exclude(pk=self.instance.user.pk)
        if user_qs.exists():
            raise ValidationError('A user account with this email already exists.')
        return email

    def save(self, commit=True):
        employee = super().save(commit=False)
        user = employee.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()

        # Update role group if changed
        role_name = self.cleaned_data.get('role')
        if role_name:
            user.groups.clear()
            group, _ = Group.objects.get_or_create(name=role_name)
            user.groups.add(group)

        if commit:
            employee.save()
        return employee

