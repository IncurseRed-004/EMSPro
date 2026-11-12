import random
from decimal import Decimal
from datetime import date, time, timedelta
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction
from departments.models import Department
from employees.models import Employee
from attendance.models import Attendance
from leaves.models import LeaveRequest


class Command(BaseCommand):
    help = 'Seeds database with roles, superuser, HR manager, employees, departments, attendance, and leaves.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting database seeding...'))
        fake = Faker()
        Faker.seed(42)
        random.seed(42)

        # 1. Create Roles / Groups
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        hr_group, _ = Group.objects.get_or_create(name='HR Manager')
        emp_group, _ = Group.objects.get_or_create(name='Employee')
        self.stdout.write(self.style.SUCCESS('Role groups created: Admin, HR Manager, Employee.'))

        # 2. Create Departments
        departments_data = [
            {'name': 'Engineering', 'description': 'Software architecture, cloud infrastructure, backend and frontend engineering.'},
            {'name': 'Human Resources', 'description': 'Talent acquisition, employee wellness, compliance, and organizational development.'},
            {'name': 'Finance & Accounts', 'description': 'Corporate finance, payroll operations, auditing, and financial reporting.'},
            {'name': 'Marketing & Sales', 'description': 'Brand positioning, client acquisition, enterprise sales, and communications.'},
            {'name': 'Product & Operations', 'description': 'Product management, agile workflows, IT support, and facilities management.'},
        ]

        departments = []
        for d in departments_data:
            dept, created = Department.objects.get_or_create(name=d['name'], defaults={'description': d['description']})
            departments.append(dept)
        self.stdout.write(self.style.SUCCESS(f'Created {len(departments)} departments.'))

        # 3. Create Key Accounts
        # 3a. Admin / Superuser
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ems.example.com',
                'first_name': 'Eleanor',
                'last_name': 'Vance',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        admin_user.groups.add(admin_group)

        admin_emp, _ = Employee.objects.get_or_create(
            user=admin_user,
            defaults={
                'first_name': 'Eleanor',
                'last_name': 'Vance',
                'email': 'admin@ems.example.com',
                'phone': '+1 555-0100',
                'gender': 'Female',
                'date_of_birth': date(1986, 4, 12),
                'address': '742 Evergreen Terrace, Springfield',
                'department': departments[0],  # Engineering
                'designation': 'VP of Engineering & Systems Admin',
                'date_of_joining': date(2021, 1, 15),
                'salary': Decimal('165000.00'),
                'employment_type': 'Full-time',
                'status': 'Active',
            }
        )

        # 3b. HR Manager
        hr_user, _ = User.objects.get_or_create(
            username='hr_user',
            defaults={
                'email': 'hr@ems.example.com',
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        hr_user.set_password('hr123')
        hr_user.save()
        hr_user.groups.add(hr_group)

        hr_emp, _ = Employee.objects.get_or_create(
            user=hr_user,
            defaults={
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'email': 'hr@ems.example.com',
                'phone': '+1 555-0145',
                'gender': 'Female',
                'date_of_birth': date(1990, 8, 22),
                'address': '108 Ocean Drive, Suite 400',
                'department': departments[1],  # Human Resources
                'designation': 'Senior HR Business Partner',
                'date_of_joining': date(2022, 3, 1),
                'salary': Decimal('98000.00'),
                'employment_type': 'Full-time',
                'status': 'Active',
            }
        )

        # 3c. Demo Employee
        emp_user, _ = User.objects.get_or_create(
            username='emp_user',
            defaults={
                'email': 'employee@ems.example.com',
                'first_name': 'David',
                'last_name': 'Miller',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        emp_user.set_password('emp123')
        emp_user.save()
        emp_user.groups.add(emp_group)

        demo_emp, _ = Employee.objects.get_or_create(
            user=emp_user,
            defaults={
                'first_name': 'David',
                'last_name': 'Miller',
                'email': 'employee@ems.example.com',
                'phone': '+1 555-0188',
                'gender': 'Male',
                'date_of_birth': date(1994, 11, 5),
                'address': '42 Wallaby Way, Sydney District',
                'department': departments[0],  # Engineering
                'designation': 'Full-Stack Software Engineer',
                'date_of_joining': date(2023, 6, 12),
                'salary': Decimal('88000.00'),
                'employment_type': 'Full-time',
                'status': 'Active',
            }
        )

        all_employees = [admin_emp, hr_emp, demo_emp]

        # 4. Generate ~22 additional realistic employees using Faker
        designation_pool = {
            'Engineering': ['Backend Engineer', 'Frontend Developer', 'DevOps Specialist', 'QA Automation Engineer', 'Cloud Architect'],
            'Human Resources': ['HR Specialist', 'Recruitment Coordinator', 'People Operations Analyst'],
            'Finance & Accounts': ['Financial Analyst', 'Payroll Specialist', 'Senior Accountant', 'Internal Auditor'],
            'Marketing & Sales': ['Marketing Strategist', 'Content Creator', 'Enterprise Account Executive', 'Sales Lead'],
            'Product & Operations': ['Product Manager', 'Scrum Master', 'IT Support Specialist', 'Operations Lead'],
        }

        genders = ['Male', 'Female', 'Other']
        employment_types = ['Full-time', 'Full-time', 'Full-time', 'Part-time', 'Contract', 'Intern']
        statuses = ['Active', 'Active', 'Active', 'Active', 'Active', 'On Leave', 'Terminated']

        for i in range(22):
            gender = random.choice(genders)
            first_name = fake.first_name_female() if gender == 'Female' else fake.first_name_male()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}"
            email = f"{username}@ems.example.com"

            # Check if user already exists
            if User.objects.filter(username=username).exists() or Employee.objects.filter(email=email).exists():
                continue

            u = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name
            )
            u.groups.add(emp_group)

            dept = random.choice(departments)
            designations = designation_pool.get(dept.name, ['Staff Associate'])
            designation = random.choice(designations)

            dob = fake.date_of_birth(minimum_age=22, maximum_age=58)
            joining_date = fake.date_between(start_date='-4y', end_date='-1m')
            salary = Decimal(str(random.randint(450, 1500) * 100))
            emp_type = random.choice(employment_types)
            status = random.choice(statuses)

            emp = Employee.objects.create(
                user=u,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=fake.phone_number()[:20],
                gender=gender,
                date_of_birth=dob,
                address=fake.address(),
                department=dept,
                designation=designation,
                date_of_joining=joining_date,
                salary=salary,
                employment_type=emp_type,
                status=status
            )
            all_employees.append(emp)

        self.stdout.write(self.style.SUCCESS(f'Total employees in database: {len(all_employees)}'))

        # 5. Assign Department Heads
        departments[0].head = admin_emp  # Engineering
        departments[0].save()
        departments[1].head = hr_emp     # HR
        departments[1].save()

        # For remaining 3 departments, pick an active employee in that department if available
        for d in departments[2:]:
            dept_active_emps = [e for e in all_employees if e.department == d and e.status == 'Active']
            if dept_active_emps:
                d.head = dept_active_emps[0]
                d.save()

        self.stdout.write(self.style.SUCCESS('Assigned department heads.'))

        # 6. Generate 30 days of attendance for active employees
        self.stdout.write(self.style.NOTICE('Generating attendance history for past 30 days...'))
        today = date.today()
        attendance_created_count = 0

        active_emps = [e for e in all_employees if e.status in ['Active', 'On Leave']]

        for days_back in range(30, -1, -1):
            target_date = today - timedelta(days=days_back)
            # Skip weekends (Saturday=5, Sunday=6)
            if target_date.weekday() >= 5:
                continue

            for emp in active_emps:
                # Check if attendance already exists
                if Attendance.objects.filter(employee=emp, date=target_date).exists():
                    continue

                # Attendance distribution: 85% Present, 8% Late, 4% Half-day, 3% Absent
                roll = random.random()
                if roll < 0.85:
                    status = 'Present'
                    check_in = time(random.randint(8, 9), random.randint(0, 29))
                    check_out = time(random.randint(17, 18), random.randint(0, 59))
                elif roll < 0.93:
                    status = 'Late'
                    check_in = time(random.randint(9, 10), random.randint(31, 55))
                    check_out = time(random.randint(18, 19), random.randint(0, 30))
                elif roll < 0.97:
                    status = 'Half-day'
                    check_in = time(9, 0)
                    check_out = time(13, random.randint(0, 30))
                else:
                    status = 'Absent'
                    check_in = None
                    check_out = None

                Attendance.objects.create(
                    employee=emp,
                    date=target_date,
                    check_in=check_in,
                    check_out=check_out,
                    status=status,
                    notes='Traffic delay' if status == 'Late' else ''
                )
                attendance_created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {attendance_created_count} attendance records.'))

        # 7. Generate Sample Leave Requests
        self.stdout.write(self.style.NOTICE('Generating sample leave requests...'))
        leave_reasons = [
            'Family vacation and personal downtime.',
            'Attending a medical appointment and recovery.',
            'Attending a cousin wedding out of state.',
            'Seasonal flu and doctor recommended bed rest.',
            'Moving to a new apartment and relocation setup.',
            'Personal emergency and family obligations.',
        ]

        leave_created_count = 0
        for emp in all_employees[:15]:
            # Create 1-2 leave requests per sample employee
            # Approved past leave
            past_start = today - timedelta(days=random.randint(15, 25))
            past_end = past_start + timedelta(days=random.randint(1, 3))
            LeaveRequest.objects.create(
                employee=emp,
                leave_type=random.choice(['Casual', 'Sick', 'Paid']),
                start_date=past_start,
                end_date=past_end,
                reason=random.choice(leave_reasons),
                status='Approved',
                reviewed_by=hr_user,
                review_remark='Approved. Enjoy your time off.'
            )
            leave_created_count += 1

            # Pending upcoming leave
            future_start = today + timedelta(days=random.randint(3, 14))
            future_end = future_start + timedelta(days=random.randint(1, 4))
            status_choice = random.choice(['Pending', 'Pending', 'Rejected'])
            LeaveRequest.objects.create(
                employee=emp,
                leave_type=random.choice(['Casual', 'Paid', 'Unpaid']),
                start_date=future_start,
                end_date=future_end,
                reason=random.choice(leave_reasons),
                status=status_choice,
                reviewed_by=hr_user if status_choice == 'Rejected' else None,
                review_remark='Denied due to peak delivery deadlines.' if status_choice == 'Rejected' else ''
            )
            leave_created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {leave_created_count} sample leave requests.'))
        self.stdout.write(self.style.SUCCESS('============================================='))
        self.stdout.write(self.style.SUCCESS('EMS Database Seeding Completed Successfully!'))
        self.stdout.write(self.style.SUCCESS('============================================='))
        self.stdout.write(self.style.NOTICE('Default Credentials:'))
        self.stdout.write(self.style.NOTICE(' - Admin:      username: admin      password: admin123'))
        self.stdout.write(self.style.NOTICE(' - HR Manager: username: hr_user    password: hr123'))
        self.stdout.write(self.style.NOTICE(' - Employee:   username: emp_user   password: emp123'))

