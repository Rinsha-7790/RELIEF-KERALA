from django import forms
from .models import Need, Camp

class NeedForm(forms.ModelForm):
    class Meta:
        model = Need
        fields = ['item', 'quantity_needed', 'quantity_received', 'unit', 'priority', 'is_fulfilled']
        labels = {
            'unit': 'Measurement Unit (e.g. kg, packets)',
        }
        help_texts = {
            'unit': 'Specify the physical unit (like kg, liters, packets, or pieces) — NOT your ward or camp unit number.',
        }
        widgets = {
            'item': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Rice, Blankets, Drinking Water'}),
            'quantity_needed': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'quantity_received': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. kg, pieces, liters'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'is_fulfilled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        show_camp = kwargs.pop('show_camp', False)
        super().__init__(*args, **kwargs)
        if show_camp:
            self.fields['camp'] = forms.ModelChoiceField(
                queryset=Camp.objects.filter(is_active=True, status='approved'),
                widget=forms.Select(attrs={'class': 'form-select'}),
                required=True
            )


class CampForm(forms.ModelForm):
    class Meta:
        model = Camp
        fields = ['name', 'location', 'district', 'people_count', 'contact_person', 'contact_phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Kazhakkoottam Relief Camp'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Govt. Higher Secondary School, Kazhakkoottam'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            'people_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Suresh Kumar'}),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10 digit phone number',
                'oninput': 'this.value=this.value.replace(/[^0-9]/g,"")',
                'maxlength': '10'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.locked_district = kwargs.pop('locked_district', None)
        super().__init__(*args, **kwargs)
        if self.locked_district:
            # Pre-fill and disable the district field so it can't be changed
            self.fields['district'].initial = self.locked_district
            self.fields['district'].widget.attrs.update({
                'disabled': True,
                'class': 'form-select bg-light text-muted',
            })
            self.fields['district'].required = False  # disabled fields aren't submitted

    def clean_district(self):
        # If district was locked (disabled), use the locked value regardless of POST data
        if self.locked_district:
            return self.locked_district
        return self.cleaned_data.get('district')