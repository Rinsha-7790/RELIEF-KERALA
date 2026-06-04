from django.urls import path
from . import views

urlpatterns = [
    path('money/', views.money_donate, name='money_donate'),
    path('items/', views.item_donate, name='item_donate'),
    path('success/', views.donation_success, name='donation_success'),
    path('payment-success/', views.payment_success, name='payment_success'),

    # Item delivery tracking
    path('panchayath-dashboard/', views.panchayath_dashboard, name='panchayath_dashboard'),
    path('panchayath-receive/<int:donation_id>/', views.panchayath_receive, name='panchayath_receive'),
    path('panchayath-dispatch/<int:donation_id>/', views.panchayath_dispatch, name='panchayath_dispatch'),

    path('camp-dashboard/', views.camp_head_dashboard, name='camp_head_dashboard'),
    path('camp-receive/<int:donation_id>/', views.camp_receive, name='camp_receive'),

    path('track/<str:tracking_id>/', views.track_donation, name='track_donation'),
    path('item-transparency/', views.item_transparency, name='item_transparency'),
    path('panchayath-deliver/<int:donation_id>/', views.panchayath_deliver, name='panchayath_deliver'),
]