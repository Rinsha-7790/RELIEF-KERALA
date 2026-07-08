from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.volunteer_register, name='volunteer_register'),
    path('success/', views.volunteer_success, name='volunteer_success'),
    path('approve/<int:pk>/', views.approve_volunteer, name='approve_volunteer'),
    path('reject/<int:pk>/', views.reject_volunteer, name='reject_volunteer'),
]