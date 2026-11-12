from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='list'),
    path('log/', views.attendance_create, name='create'),
    path('<int:pk>/edit/', views.attendance_update, name='update'),
    path('<int:pk>/delete/', views.attendance_delete, name='delete'),
    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),
    path('summary/<int:employee_id>/', views.monthly_summary, name='monthly_summary'),
]

