from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('staff-login/', views.staff_login, name='staff_login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('officials/', views.officials_portal, name='officials_portal'),
    path('register/panchayath/', views.panchayath_register, name='panchayath_register'),
    path('register/camp-head/', views.camp_head_register, name='camp_head_register'),
    path('register/field-officer/', views.field_officer_register, name='field_officer_register'),
    path('register/district-officer/', views.district_officer_register, name='district_officer_register'),
    path('camp-head/<int:user_id>/approve-panchayath/', views.approve_camp_head_panchayath, name='approve_camp_head_panchayath'),
    path('camp-head/<int:user_id>/reject-panchayath/', views.reject_camp_head_panchayath, name='reject_camp_head_panchayath'),
    path('camp-head/<int:user_id>/approve-field/', views.approve_camp_head_field_officer, name='approve_camp_head_field_officer'),
    path('camp-head/<int:user_id>/reject-field/', views.reject_camp_head_field_officer, name='reject_camp_head_field_officer'),
]