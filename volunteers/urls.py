from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.volunteer_register, name='volunteer_register'),
    path('success/', views.volunteer_success, name='volunteer_success'),
]