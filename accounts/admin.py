from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'role', 'panchayath_name', 'district', 'phone', 'is_staff']
    list_filter   = ['role', 'is_staff', 'district']
    search_fields = ['username', 'email', 'panchayath_name', 'district']

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Role & Contact', {
            'fields': ('role', 'phone', 'email')
        }),
        ('Panchayath Details', {
            'fields': (
                'panchayath_name',
                'district',
                'office_address',
                'contact_person',
            ),
            'description': 'Fill these only for Panchayath Staff accounts'
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'phone',
                       'panchayath_name', 'district', 'office_address', 'contact_person'),
        }),
    )