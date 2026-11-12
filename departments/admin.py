from django.contrib import admin
from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'head', 'get_employee_count', 'created_at')
    search_fields = ('name', 'description')
    list_select_related = ('head',)

    def get_employee_count(self, obj):
        return obj.employees.count()
    get_employee_count.short_description = 'Employees'
