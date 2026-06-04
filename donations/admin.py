from django.contrib import admin
from django.utils import timezone
from .models import MoneyDonation, ItemDonation


@admin.register(MoneyDonation)
class MoneyDonationAdmin(admin.ModelAdmin):
    list_display  = ['donor_name', 'amount', 'camp', 'status', 'date']
    list_filter   = ['status', 'camp']
    search_fields = ['donor_name']


@admin.register(ItemDonation)
class ItemDonationAdmin(admin.ModelAdmin):
    list_display  = [
        'tracking_id', 'donor_name', 'item_name',
        'quantity', 'unit', 'camp', 'delivery_status', 'created_at'
    ]
    list_filter   = ['delivery_status', 'camp']
    search_fields = ['donor_name', 'item_name', 'tracking_id']

    # Allow editing status directly from the list page
    list_editable = ['delivery_status']

    # Organise the detail page into sections
    fieldsets = (
        ('Donor Info', {
            'fields': ('donor', 'donor_name', 'donor_phone')
        }),
        ('Item Details', {
            'fields': ('item_name', 'quantity', 'unit', 'camp', 'tracking_id')
        }),
        ('Delivery Status', {
            'fields': ('delivery_status',),
            'description': 'Update the current stage of this donation delivery.'
        }),
        ('Panchayath Stage', {
            'fields': ('panchayath_name', 'panchayath_address'),
            'classes': ('collapse',),
        }),
        ('Dispatch Stage', {
            'fields': ('dispatched_by', 'dispatched_at'),
            'classes': ('collapse',),
        }),
        ('Camp Receipt Stage', {
            'fields': ('received_by', 'received_at'),
            'classes': ('collapse',),
        }),
        ('Notes', {
            'fields': ('delivery_notes',),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ['tracking_id', 'created_at']

    # Admin actions to bulk update status
    actions = [
        'mark_at_panchayath',
        'mark_in_transit',
        'mark_at_camp',
        'mark_delivered',
    ]

    def mark_at_panchayath(self, request, queryset):
        queryset.update(delivery_status='at_panchayath')
        self.message_user(request, f"{queryset.count()} donation(s) marked as At Panchayath.")
    mark_at_panchayath.short_description = "Mark selected as → At Panchayath"

    def mark_in_transit(self, request, queryset):
        queryset.update(
            delivery_status='in_transit',
            dispatched_at=timezone.now()
        )
        self.message_user(request, f"{queryset.count()} donation(s) marked as In Transit.")
    mark_in_transit.short_description = "Mark selected as → In Transit"

    def mark_at_camp(self, request, queryset):
        queryset.update(
            delivery_status='at_camp',
            received_at=timezone.now()
        )
        self.message_user(request, f"{queryset.count()} donation(s) marked as At Camp.")
    mark_at_camp.short_description = "Mark selected as → At Camp"

    def mark_delivered(self, request, queryset):
        queryset.update(
            delivery_status='delivered',
            received_at=timezone.now()
        )
        self.message_user(request, f"{queryset.count()} donation(s) marked as Delivered.")
    mark_delivered.short_description = "Mark selected as → Delivered ✓"