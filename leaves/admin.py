from django.contrib import admin
from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'leave_type',
        'start_date',
        'end_date',
        'duration_days',
        'status',
        'reviewed_by',
        'applied_on'
    )
    list_filter = ('status', 'leave_type', 'applied_on')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_id', 'reason')
    list_select_related = ('employee', 'reviewed_by')
    readonly_fields = ('applied_on', 'updated_at')
