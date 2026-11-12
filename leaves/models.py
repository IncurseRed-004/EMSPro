from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('Casual', 'Casual Leave'),
        ('Sick', 'Sick Leave'),
        ('Paid', 'Paid Leave'),
        ('Unpaid', 'Unpaid Leave'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, default='Casual')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leaves'
    )
    review_remark = models.TextField(blank=True)
    applied_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_on']

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type} ({self.start_date} to {self.end_date}) [{self.status}]"

    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def clean(self):
        super().clean()
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({'end_date': 'End date cannot be earlier than start date.'})

            # Check for overlapping leave requests for this employee (excluding this record and Rejected ones)
            if hasattr(self, 'employee_id') and self.employee_id:
                overlapping = LeaveRequest.objects.filter(
                    employee_id=self.employee_id,
                    status__in=['Pending', 'Approved'],
                    start_date__lte=self.end_date,
                    end_date__gte=self.start_date
                )
                if self.pk:
                    overlapping = overlapping.exclude(pk=self.pk)

                if overlapping.exists():
                    conflict = overlapping.first()
                    raise ValidationError(
                        f'Leave request conflicts with an existing {conflict.status.lower()} leave '
                        f'from {conflict.start_date} to {conflict.end_date}.'
                    )
