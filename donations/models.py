from django.db import models
from django.conf import settings
from camps.models import Camp

class MoneyDonation(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('allocated', 'Allocated to Camp'),
        ('spent', 'Spent'),
    ]
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    donor_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    camp = models.ForeignKey(Camp, on_delete=models.SET_NULL, null=True, blank=True)
    purpose = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"₹{self.amount} by {self.donor_name}"


DELIVERY_STATUS_CHOICES = [
    ('registered',    'Registered'),
    ('at_panchayath', 'At Panchayath'),
    ('in_transit',    'In Transit'),
    ('at_camp',       'Received at Camp'),
    ('delivered',     'Delivered'),
]

class ItemDonation(models.Model):
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    donor_name    = models.CharField(max_length=100)
    donor_phone   = models.CharField(max_length=15)
    item_name     = models.CharField(max_length=200)
    quantity      = models.PositiveIntegerField(default=1)
    unit          = models.CharField(max_length=50, blank=True)
    camp          = models.ForeignKey(Camp, on_delete=models.SET_NULL, null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    delivery_status    = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='registered')
    panchayath_name    = models.CharField(max_length=150, blank=True)
    panchayath_address = models.TextField(blank=True)
    dispatched_by      = models.CharField(max_length=150, blank=True)
    dispatched_at      = models.DateTimeField(null=True, blank=True)
    received_by        = models.CharField(max_length=150, blank=True)
    received_at        = models.DateTimeField(null=True, blank=True)
    delivery_notes     = models.TextField(blank=True)
    tracking_id        = models.CharField(max_length=20, blank=True)
    panchayath = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'panchayath_staff'},
        related_name='assigned_donations',
    )

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            import random, string
            self.tracking_id = 'KR' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.item_name}"