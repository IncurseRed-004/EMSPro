from datetime import datetime, date
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Half-day', 'Half-day'),
        ('Late', 'Late'),
    ]

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField(default=timezone.localdate)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Present'
    )
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-check_in']
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} ({self.status})"

    def clean(self):
        super().clean()
        if self.check_in and self.check_out and self.check_out <= self.check_in:
            raise ValidationError({'check_out': 'Check-out time must be after check-in time.'})

    @property
    def duration_hours(self):
        if self.check_in and self.check_out:
            dummy_date = date(2000, 1, 1)
            t1 = datetime.combine(dummy_date, self.check_in)
            t2 = datetime.combine(dummy_date, self.check_out)
            delta = t2 - t1
            return round(delta.total_seconds() / 3600.0, 2)
        return None
