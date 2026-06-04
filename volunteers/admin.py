from django.contrib import admin
from .models import VolunteerProfile

@admin.register(VolunteerProfile)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'phone', 'location',
        'profession', 'is_approved', 'registered_at'
    ]
    list_filter = [
        'is_approved', 'profession', 'gender',
        'has_nss', 'has_ncc', 'has_ngo',
        'has_first_aid', 'has_swimming', 'has_driving'
    ]
    search_fields = ['full_name', 'phone', 'location', 'skills']
    readonly_fields = ['registered_at']
    actions = ['approve_volunteers']

    fieldsets = (
        ('Personal Info', {
            'fields': ('user', 'full_name', 'phone', 'age', 'gender', 'address', 'location')
        }),
        ('Professional Info', {
            'fields': ('profession', 'organization')
        }),
        ('Organisation Memberships', {
            'fields': ('has_nss', 'has_ncc', 'has_ngo', 'has_scouts', 'has_red_cross', 'has_civil_defence', 'other_organisation')
        }),
        ('Skills', {
            'fields': ('skills', 'help_types', 'has_first_aid', 'has_swimming', 'has_driving', 'languages')
        }),
        ('Availability', {
            'fields': ('available_from', 'available_until', 'full_time')
        }),
        ('ID & Status', {
            'fields': ('id_proof_number', 'is_approved', 'assigned_camp', 'registered_at')
        }),
    )

    def approve_volunteers(self, request, queryset):
        queryset.update(is_approved=True)
    approve_volunteers.short_description = 'Approve selected volunteers'