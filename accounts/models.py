from django.contrib.auth.models import AbstractUser
from django.db import models

KERALA_DISTRICTS = [
    ('Thiruvananthapuram', 'Thiruvananthapuram'),
    ('Kollam', 'Kollam'),
    ('Pathanamthitta', 'Pathanamthitta'),
    ('Alappuzha', 'Alappuzha'),
    ('Kottayam', 'Kottayam'),
    ('Idukki', 'Idukki'),
    ('Ernakulam', 'Ernakulam'),
    ('Thrissur', 'Thrissur'),
    ('Palakkad', 'Palakkad'),
    ('Malappuram', 'Malappuram'),
    ('Kozhikode', 'Kozhikode'),
    ('Wayanad', 'Wayanad'),
    ('Kannur', 'Kannur'),
    ('Kasaragod', 'Kasaragod'),
]

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('donor',            'Donor'),
        ('volunteer',        'Volunteer'),
        ('admin',            'Admin'),
        ('panchayath_staff', 'Panchayath Staff'),
    ]
    role             = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')
    phone            = models.CharField(max_length=15, blank=True)

    # Panchayath fields (only filled when role = panchayath_staff)
    panchayath_name  = models.CharField(max_length=200, blank=True)
    district         = models.CharField(max_length=50, choices=KERALA_DISTRICTS, blank=True)
    office_address   = models.TextField(blank=True)
    contact_person   = models.CharField(max_length=100, blank=True)

    def __str__(self):
        if self.role == 'panchayath_staff':
            return f"{self.panchayath_name} ({self.district})"
        return f"{self.username} ({self.role})"

    def is_admin_user(self):
        return self.role == 'admin'