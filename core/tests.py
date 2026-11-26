from decimal import Decimal
from datetime import date
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group, AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from core.decorators import role_required, verify_employee_ownership
from core.context_processors import role_context
from core.views import custom_permission_denied_view, custom_page_not_found_view, custom_server_error_view
from departments.models import Department
from employees.models import Employee


class CoreDecoratorsAndContextTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_group = Group.objects.create(name='Admin')
        self.hr_group = Group.objects.create(name='HR Manager')
        self.emp_group = Group.objects.create(name='Employee')

        self.dept = Department.objects.create(name='Engineering')

        self.user = User.objects.create_user(username='john', email='john@test.com', password='password123')
        self.user.groups.add(self.emp_group)

        self.emp = Employee.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john@test.com',
            phone='+1 555-0100',
            date_of_birth=date(1990, 1, 1),
            department=self.dept,
            designation='Engineer',
            date_of_joining=date(2022, 1, 1),
            salary=Decimal('70000.00'),
            employment_type='Full-time',
            status='Active'
        )

        self.hr_user = User.objects.create_user(username='hr_admin', email='hr@test.com', password='password123')
        self.hr_user.groups.add(self.hr_group)

        self.superuser = User.objects.create_superuser(username='super', email='super@test.com', password='password123')

    def test_role_context_without_user_attribute(self):
        request = self.factory.get('/')
        # request without .user attribute (as created by RequestFactory before middleware)
        ctx = role_context(request)
        self.assertEqual(ctx['user_role'], 'Anonymous')
        self.assertFalse(ctx['is_admin'])
        self.assertFalse(ctx['is_hr'])
        self.assertFalse(ctx['is_admin_or_hr'])
        self.assertIsNone(ctx['user_employee'])

    def test_role_context_anonymous(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        ctx = role_context(request)
        self.assertEqual(ctx['user_role'], 'Anonymous')
        self.assertFalse(ctx['is_admin'])
        self.assertFalse(ctx['is_hr'])
        self.assertFalse(ctx['is_admin_or_hr'])
        self.assertIsNone(ctx['user_employee'])

    def test_role_context_employee(self):
        request = self.factory.get('/')
        request.user = self.user
        ctx = role_context(request)
        self.assertEqual(ctx['user_role'], 'Employee')
        self.assertFalse(ctx['is_admin'])
        self.assertFalse(ctx['is_hr'])
        self.assertEqual(ctx['user_employee'], self.emp)

    def test_role_context_admin(self):
        request = self.factory.get('/')
        request.user = self.superuser
        ctx = role_context(request)
        self.assertEqual(ctx['user_role'], 'Admin')
        self.assertTrue(ctx['is_admin'])
        self.assertTrue(ctx['is_admin_or_hr'])

    def test_role_required_decorator_allows_authorized_role(self):
        @role_required('Employee')
        def dummy_view(request):
            return HttpResponse('OK')

        request = self.factory.get('/')
        request.user = self.user
        response = dummy_view(request)
        self.assertEqual(response.status_code, 200)

    def test_role_required_decorator_denies_unauthorized_role(self):
        @role_required('Admin')
        def admin_view(request):
            return HttpResponse('Admin Only')

        request = self.factory.get('/')
        request.user = self.user
        with self.assertRaises(PermissionDenied):
            admin_view(request)

    def test_verify_employee_ownership(self):
        request = self.factory.get('/')
        request.user = self.user
        # John owns John's record
        self.assertTrue(verify_employee_ownership(request, self.emp))

        # Other user trying to access John's record
        other_user = User.objects.create_user(username='other', email='other@test.com', password='password123')
        request.user = other_user
        with self.assertRaises(PermissionDenied):
            verify_employee_ownership(request, self.emp)

        # HR can access John's record
        request.user = self.hr_user
        self.assertTrue(verify_employee_ownership(request, self.emp))

        # Superuser can access John's record
        request.user = self.superuser
        self.assertTrue(verify_employee_ownership(request, self.emp))

    def test_custom_error_views(self):
        request = self.factory.get('/')
        res403 = custom_permission_denied_view(request)
        self.assertEqual(res403.status_code, 403)

        res404 = custom_page_not_found_view(request)
        self.assertEqual(res404.status_code, 404)

        res500 = custom_server_error_view(request)
        self.assertEqual(res500.status_code, 500)
