from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from departments.models import Department
from employees.models import Employee


class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_group = Group.objects.create(name='Admin')
        self.emp_group = Group.objects.create(name='Employee')

        self.admin_user = User.objects.create_superuser(
            username='admin_dash',
            email='admin_dash@test.com',
            password='pass'
        )
        self.admin_user.groups.add(self.admin_group)

        self.dept = Department.objects.create(name='Marketing')
        self.emp_user = User.objects.create_user(username='emp_dash', email='emp_dash@test.com', password='pass')
        self.emp_user.groups.add(self.emp_group)
        self.emp = Employee.objects.create(
            user=self.emp_user,
            first_name='Bruce',
            last_name='Wayne',
            email='emp_dash@test.com',
            phone='+1 555-0109',
            date_of_birth=date(1990, 2, 19),
            department=self.dept,
            designation='Executive',
            date_of_joining=date(2021, 5, 1),
            salary=Decimal('120000.00'),
            employment_type='Full-time',
            status='Active'
        )

    def test_anonymous_redirect_to_login(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_admin_dashboard_renders(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Executive Dashboard')
        self.assertContains(response, 'Attendance Trend')

    def test_employee_dashboard_renders(self):
        self.client.force_login(self.emp_user)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Today's Attendance")
        self.assertContains(response, 'Leave Quota Balances')
