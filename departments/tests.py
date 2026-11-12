from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from departments.models import Department


class DepartmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_group = Group.objects.create(name='Admin')
        self.emp_group = Group.objects.create(name='Employee')

        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='pass'
        )
        self.admin_user.groups.add(self.admin_group)

        self.regular_user = User.objects.create_user(
            username='reg_test',
            email='reg@test.com',
            password='pass'
        )
        self.regular_user.groups.add(self.emp_group)

        self.dept = Department.objects.create(
            name='Engineering',
            description='Tech team'
        )

    def test_department_list_accessible_by_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('departments:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Engineering')

    def test_department_list_forbidden_for_regular_employee(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse('departments:list'))
        self.assertEqual(response.status_code, 403)

    def test_department_create(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('departments:create'), {
            'name': 'Marketing',
            'description': 'Marketing division',
            'head': ''
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Department.objects.filter(name='Marketing').exists())

    def test_department_delete(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('departments:delete', kwargs={'pk': self.dept.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Department.objects.filter(name='Engineering').exists())
