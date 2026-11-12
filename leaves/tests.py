from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from departments.models import Department
from employees.models import Employee
from leaves.models import LeaveRequest


class LeavesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hr_group = Group.objects.create(name='HR Manager')
        self.emp_group = Group.objects.create(name='Employee')

        self.dept = Department.objects.create(name='HR')

        # HR user
        self.hr_user = User.objects.create_user(username='hr_tester', email='hr_tester@test.com', password='pass')
        self.hr_user.groups.add(self.hr_group)

        # Employee user
        self.emp_user = User.objects.create_user(username='emp_tester', email='emp_tester@test.com', password='pass')
        self.emp_user.groups.add(self.emp_group)
        self.emp = Employee.objects.create(
            user=self.emp_user,
            first_name='Peter',
            last_name='Parker',
            email='emp_tester@test.com',
            phone='+1 555-0106',
            date_of_birth=date(1996, 8, 10),
            department=self.dept,
            designation='Photographer',
            date_of_joining=date(2023, 3, 1),
            salary=Decimal('50000.00'),
            employment_type='Full-time',
            status='Active'
        )

    def test_apply_leave_success(self):
        self.client.force_login(self.emp_user)
        start = date.today() + timedelta(days=5)
        end = date.today() + timedelta(days=7)
        response = self.client.post(reverse('leaves:apply'), {
            'leave_type': 'Casual',
            'start_date': start.strftime('%Y-%m-%d'),
            'end_date': end.strftime('%Y-%m-%d'),
            'reason': 'Vacation trip',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(LeaveRequest.objects.filter(employee=self.emp, status='Pending').exists())

    def test_hr_leave_review_approval(self):
        leave = LeaveRequest.objects.create(
            employee=self.emp,
            leave_type='Sick',
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=11),
            reason='Medical procedure',
            status='Pending'
        )

        self.client.force_login(self.hr_user)
        response = self.client.post(reverse('leaves:review', kwargs={'pk': leave.pk}), {
            'status': 'Approved',
            'review_remark': 'Approved as requested.'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        leave.refresh_from_db()
        self.assertEqual(leave.status, 'Approved')
        self.assertEqual(leave.reviewed_by, self.hr_user)

    def test_employee_cancel_pending_leave(self):
        leave = LeaveRequest.objects.create(
            employee=self.emp,
            leave_type='Casual',
            start_date=date.today() + timedelta(days=20),
            end_date=date.today() + timedelta(days=21),
            reason='Change of plans',
            status='Pending'
        )
        self.client.force_login(self.emp_user)
        response = self.client.post(reverse('leaves:cancel', kwargs={'pk': leave.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(LeaveRequest.objects.filter(pk=leave.pk).exists())
