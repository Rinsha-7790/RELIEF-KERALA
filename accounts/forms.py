from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import uuid

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'})
    )
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Your first name'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Your last name'})
    )
    phone = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '10 digit mobile number',
            'oninput': 'this.value=this.value.replace(/[^0-9]/g,"")',
            'maxlength': '10'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("A user with this email address already exists.")
        return email

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email',
                  'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        base_username = self.cleaned_data['email'].split('@')[0]
        username = base_username
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username}_{str(uuid.uuid4())[:4]}"
        user.username  = username
        user.email     = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.phone     = self.cleaned_data['phone']
        user.role      = 'donor'
        if commit:
            user.save()
        return user