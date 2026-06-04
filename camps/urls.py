from django.urls import path
from . import views

urlpatterns = [
    path('', views.camp_list, name='camp_list'),
    path('<int:pk>/', views.camp_detail, name='camp_detail'),
    path('map/', views.camp_map, name='camp_map'),
]