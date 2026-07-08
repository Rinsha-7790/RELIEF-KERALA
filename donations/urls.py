from django.urls import path
from . import views

urlpatterns = [
    path('money/', views.money_donate, name='money_donate'),
    path('items/', views.item_donate, name='item_donate'),
    path('success/', views.donation_success, name='donation_success'),
    path('payment-success/', views.payment_success, name='payment_success'),

    # Panchayath
    path('panchayath-receive/<int:donation_id>/', views.panchayath_receive, name='panchayath_receive'),
    path('panchayath-dispatch/<int:donation_id>/', views.panchayath_dispatch, name='panchayath_dispatch'),

    # Camp head
    path('camp-confirm/<int:donation_id>/', views.camp_confirm_delivery, name='camp_confirm_delivery'),

    # Public
    path('track/<str:tracking_id>/', views.track_donation, name='track_donation'),
    path('item-transparency/', views.item_transparency, name='item_transparency'),
    path('update/<str:tracking_id>/', views.public_update, name='public_update'),
]