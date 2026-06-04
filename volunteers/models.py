from django.db import models
from django.conf import settings
from camps.models import Camp

class VolunteerProfile(models.Model):

    PROFESSION_CHOICES = [
        ('student', 'Student'),
        ('doctor', 'Doctor / Medical Professional'),
        ('nurse', 'Nurse / Paramedic'),
        ('engineer', 'Engineer'),
        ('teacher', 'Teacher'),
        ('driver', 'Driver'),
        ('cook', 'Cook'),
        ('social_worker', 'Social Worker'),
        ('govt_employee', 'Government Employee'),
        ('ngo_worker', 'NGO Worker'),
        ('police', 'Police / Military'),
        ('other', 'Other'),
    ]

    # Basic Info
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    full_name = models.CharField(max_length=200, default='')
    phone = models.CharField(max_length=10, default='')
    age = models.PositiveIntegerField(default=18)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], default='other')
    address = models.TextField(default='')
    location = models.CharField(max_length=200, default='')

    # Professional Info
    profession = models.CharField(
        max_length=50,
        choices=PROFESSION_CHOICES,
        default='other'
    )
    organization = models.CharField(max_length=200, blank=True, default='')

    # Organisation memberships
    has_nss = models.BooleanField(default=False, verbose_name='NSS Member')
    has_ncc = models.BooleanField(default=False, verbose_name='NCC Member')
    has_ngo = models.BooleanField(default=False, verbose_name='NGO Member')
    has_scouts = models.BooleanField(default=False, verbose_name='Scouts / Guides')
    has_red_cross = models.BooleanField(default=False, verbose_name='Red Cross')
    has_civil_defence = models.BooleanField(default=False, verbose_name='Civil Defence')
    other_organisation = models.CharField(max_length=200, blank=True, default='')

    # Skills
    skills = models.CharField(max_length=500, default='')
    help_types = models.CharField(max_length=500, default='')
    has_first_aid = models.BooleanField(default=False, verbose_name='First Aid Trained')
    has_swimming = models.BooleanField(default=False, verbose_name='Can Swim')
    has_driving = models.BooleanField(default=False, verbose_name='Has Driving License')
    languages = models.CharField(max_length=200, default='Malayalam, English')

    # Availability
    available_from = models.DateField(null=True, blank=True)
    available_until = models.DateField(null=True, blank=True)
    full_time = models.BooleanField(default=False, verbose_name='Available Full Time')

    # ID
    id_proof_number = models.CharField(max_length=100, default='')

    # Status
    is_approved = models.BooleanField(default=False)
    assigned_camp = models.ForeignKey(
        Camp,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='volunteers'
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.location})"