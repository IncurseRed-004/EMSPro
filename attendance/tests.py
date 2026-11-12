from decimal import Decimal
from datetime import date, time
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from departments.models import Department
from employees.models import Employee
from attendance.models import Attendance


class AttendanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.emp_group = Group.objects.create(name='Employee')
        self.admin_group = Group.objects.create(name='Admin')

        self.user = User.objects.create_user(username='att_user', email='att@test.com', password='pass')
        self.user.groups.add(self.emp_group)

        self.dept = Department.objects.create(name='Ops')
        self.employee = Employee.objects.create(
            user=self.user,
            first_name='Clara',
            last_name='Oswald',
            email='att@test.com',
            phone='+1 555-0105',
            date_of_birth=date(1993, 10, 5),
            department=self.dept,
            designation='Specialist',
            date_of_joining=date(2023, 1, 15),
            salary=Decimal('60000.00'),
            employment_type='Full-time',
            status='Active'
        )

    def test_check_in_and_check_out_flow(self):
        self.client.force_login(self.user)

        # 1. Check in
        res1 = self.client.post(reverse('attendance:check_in'), follow=True)
        self.assertEqual(res1.status_code, 200)

        record = Attendance.objects.get(employee=self.employee, date=date.today())
        self.assertIsNotNone(record.check_in)

        # 2. Check out
        res2 = self.client.post(reverse('attendance:check_out'), follow=True)
        self.assertEqual(res2.status_code, 200)

        record.refresh_from_db()
        self.assertIsNotNone(record.check_out)

    def test_monthly_summary_renders(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('attendance:monthly_summary', kwargs={'employee_id': self.employee.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Monthly Attendance Summary')
