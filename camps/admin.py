from django.contrib import admin
from django import forms
from .models import Camp, Need, EmergencyAlert

class CampAdminForm(forms.ModelForm):
    contact_phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'pattern': '[0-9]{10}',
            'placeholder': '9876543210',
            'oninput': 'this.value = this.value.replace(/[^0-9]/g, "")',
            'inputmode': 'numeric',
        })
    )
    class Meta:
        model = Camp
        fields = '__all__'

class NeedInline(admin.TabularInline):
    model = Need
    extra = 3

@admin.register(Camp)
class CampAdmin(admin.ModelAdmin):
    form = CampAdminForm
    list_display = ['name', 'district', 'people_count', 'is_active', 'updated_at']
    list_filter = ['is_active', 'district']
    search_fields = ['name', 'location']
    inlines = [NeedInline]

@admin.register(Need)
class NeedAdmin(admin.ModelAdmin):
    list_display = ['item', 'camp', 'quantity_needed', 'quantity_received', 'priority', 'is_fulfilled']
    list_filter = ['priority', 'is_fulfilled']

@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ['message', 'level', 'is_active', 'created_at']
    list_filter = ['level', 'is_active']