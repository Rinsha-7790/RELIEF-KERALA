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
        ('donor',              'Donor'),
        ('volunteer',          'Volunteer'),
        ('admin',              'Admin'),
        ('panchayath_staff',   'Panchayath Officer'),
        ('field_officer',      'Field Officer'),
        ('district_officer',   'District Officer'),
        ('camp_head',          'Camp Head'),
    ]
    role           = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')
    phone          = models.CharField(max_length=15, blank=True)

    # Panchayath fields
    panchayath_name = models.CharField(max_length=200, blank=True)
    district        = models.CharField(max_length=50, choices=KERALA_DISTRICTS, blank=True)
    office_address  = models.TextField(blank=True)
    contact_person  = models.CharField(max_length=100, blank=True)

    # Camp head fields
    camp = models.ForeignKey(
        'camps.Camp',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='camp_heads'
    )

    # Verification & validation fields for staff
    employee_id = models.CharField(max_length=50, blank=True)
    id_proof    = models.FileField(upload_to='id_proofs/', blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    approved_by_panchayath    = models.BooleanField(default=False)
    approved_by_field_officer = models.BooleanField(default=False)

    def __str__(self):
        if self.role == 'panchayath_staff':
            return f"{self.panchayath_name} ({self.district})"
        if self.role == 'camp_head':
            return f"Camp Head — {self.camp.name if self.camp else 'No Camp'}"
        return f"{self.username} ({self.role})"

    def is_admin_user(self):
        return self.role == 'admin'


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login',             'Login'),
        ('logout',            'Logout'),
        ('register',          'Registration'),
        ('approve_staff',     'Staff Approved'),
        ('reject_staff',      'Staff Rejected'),
        ('approve_volunteer', 'Volunteer Approved'),
        ('allocate_funds',    'Funds Allocated'),
        ('add_camp',          'Camp Added'),
        ('update_camp',       'Camp Updated'),
        ('add_need',          'Need Reported'),
        ('verify_need',       'Need Verified'),
        ('donate_money',      'Money Donated'),
        ('donate_item',       'Item Donated'),
        ('update_delivery',   'Delivery Updated'),
        ('other',             'Other'),
    ]

    performed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs'
    )
    action      = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    target_user = models.CharField(max_length=150, blank=True, help_text="Username of the affected user, if any")
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    extra_data  = models.JSONField(null=True, blank=True, help_text="Any additional structured info")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        actor = self.performed_by.username if self.performed_by else 'System'
        return f"[{self.timestamp:%d %b %Y %H:%M}] {actor} — {self.get_action_display()}"


def log_action(request, action, description, target_user='', extra_data=None):
    """
    Helper to create an AuditLog entry from any view.
    Usage:
        from accounts.models import log_action
        log_action(request, 'approve_staff', 'Approved panchayath user john', target_user='john')
    """
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', None))
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()
    AuditLog.objects.create(
        performed_by=request.user if request.user.is_authenticated else None,
        action=action,
        description=description,
        target_user=target_user,
        ip_address=ip,
        extra_data=extra_data,
    )