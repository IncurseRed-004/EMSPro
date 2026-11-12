from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from departments.models import Department
from employees.models import Employee


class EmployeeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_group = Group.objects.create(name='Admin')
        self.hr_group = Group.objects.create(name='HR Manager')
        self.emp_group = Group.objects.create(name='Employee')

        self.admin_user = User.objects.create_superuser(
            username='admin_emp_test',
            email='admin_emp@test.com',
            password='pass'
        )
        self.admin_user.groups.add(self.admin_group)

        self.dept = Department.objects.create(name='Tech', description='Tech Dept')

        # Employee 1
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='pass')
        self.user1.groups.add(self.emp_group)
        self.emp1 = Employee.objects.create(
            user=self.user1,
            first_name='Alice',
            last_name='Smith',
            email='user1@test.com',
            phone='+1 555-0101',
            date_of_birth=date(1992, 5, 10),
            department=self.dept,
            designation='Engineer',
            date_of_joining=date(2022, 1, 10),
            salary=Decimal('75000.00'),
            employment_type='Full-time',
            status='Active'
        )

        # Employee 2
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='pass')
        self.user2.groups.add(self.emp_group)
        self.emp2 = Employee.objects.create(
            user=self.user2,
            first_name='Bob',
            last_name='Jones',
            email='user2@test.com',
            phone='+1 555-0102',
            date_of_birth=date(1995, 3, 14),
            department=self.dept,
            designation='Designer',
            date_of_joining=date(2023, 2, 1),
            salary=Decimal('65000.00'),
            employment_type='Full-time',
            status='Active'
        )

    def test_auto_employee_id_generation(self):
        self.assertTrue(self.emp1.employee_id.startswith('EMP-'))
        self.assertTrue(self.emp2.employee_id.startswith('EMP-'))
        self.assertNotEqual(self.emp1.employee_id, self.emp2.employee_id)

    def test_employee_ownership_permission(self):
        # Alice can view her own profile
        self.client.force_login(self.user1)
        res1 = self.client.get(reverse('employees:detail', kwargs={'pk': self.emp1.pk}))
        self.assertEqual(res1.status_code, 200)

        # Alice cannot view Bob's profile
        res2 = self.client.get(reverse('employees:detail', kwargs={'pk': self.emp2.pk}))
        self.assertEqual(res2.status_code, 403)

        # Admin can view Bob's profile
        self.client.force_login(self.admin_user)
        res3 = self.client.get(reverse('employees:detail', kwargs={'pk': self.emp2.pk}))
        self.assertEqual(res3.status_code, 200)

    def test_employee_export_csv(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('employees:export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertContains(response, 'Alice')
        self.assertContains(response, 'Bob')

    def test_employee_deactivate(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('employees:deactivate', kwargs={'pk': self.emp2.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.emp2.refresh_from_db()
        self.assertEqual(self.emp2.status, 'Terminated')
