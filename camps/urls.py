from django.urls import path
from . import views

urlpatterns = [
    path('', views.camp_list, name='camp_list'),
    path('<int:pk>/', views.camp_detail, name='camp_detail'),
    path('map/', views.camp_map, name='camp_map'),
    path('create/', views.create_camp, name='create_camp'),
    path('verify/<int:pk>/', views.verify_camp, name='verify_camp'),
    path('approve/<int:pk>/', views.approve_camp, name='approve_camp'),
    path('need/add/', views.add_need, name='add_need'),
    path('need/<int:pk>/edit/', views.edit_need, name='edit_need'),
    path('need/<int:pk>/delete/', views.delete_need, name='delete_need'),
    path('need/<int:pk>/toggle/', views.toggle_need_fulfillment, name='toggle_need_fulfillment'),
    path('need/<int:pk>/verify/', views.verify_need, name='verify_need'),
    path('need/<int:pk>/reject/', views.reject_need, name='reject_need'),
]