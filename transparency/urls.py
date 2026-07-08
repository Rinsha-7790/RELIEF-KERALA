from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('allocate-funds/', views.allocate_funds, name='allocate_funds'),
    path('approve-staff/<int:user_id>/', views.approve_staff, name='approve_staff'),
    path('reject-staff/<int:user_id>/', views.reject_staff, name='reject_staff'),
]