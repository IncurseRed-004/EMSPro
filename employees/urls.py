from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.employee_list, name='list'),
    path('create/', views.employee_create, name='create'),
    path('export/csv/', views.employee_export_csv, name='export_csv'),
    path('<int:pk>/', views.employee_detail, name='detail'),
    path('<int:pk>/edit/', views.employee_update, name='update'),
    path('<int:pk>/delete/', views.employee_delete, name='delete'),
    path('<int:pk>/deactivate/', views.employee_deactivate, name='deactivate'),
]

