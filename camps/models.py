from django.db import models

KERALA_DISTRICTS = [
    ('Alappuzha', 'Alappuzha'),
    ('Ernakulam', 'Ernakulam'),
    ('Idukki', 'Idukki'),
    ('Kannur', 'Kannur'),
    ('Kasaragod', 'Kasaragod'),
    ('Kollam', 'Kollam'),
    ('Kottayam', 'Kottayam'),
    ('Kozhikode', 'Kozhikode'),
    ('Malappuram', 'Malappuram'),
    ('Palakkad', 'Palakkad'),
    ('Pathanamthitta', 'Pathanamthitta'),
    ('Thiruvananthapuram', 'Thiruvananthapuram'),
    ('Thrissur', 'Thrissur'),
    ('Wayanad', 'Wayanad'),
]

class Camp(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)
    district = models.CharField(
        max_length=100,
        choices=KERALA_DISTRICTS,
        default='Kozhikode'
    )
    people_count = models.PositiveIntegerField(default=0)
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.district}"


class Need(models.Model):
    PRIORITY_CHOICES = [
        ('urgent', 'Urgent'),
        ('normal', 'Normal'),
        ('low', 'Low'),
    ]
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name='needs')
    item = models.CharField(max_length=200)
    quantity_needed = models.PositiveIntegerField()
    quantity_received = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=50, default='units')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    is_fulfilled = models.BooleanField(default=False)

    def remaining(self):
        return max(self.quantity_needed - self.quantity_received, 0)

    def percent_fulfilled(self):
        if self.quantity_needed == 0:
            return 100
        return int((self.quantity_received / self.quantity_needed) * 100)

    def __str__(self):
        return f"{self.item} for {self.camp.name}"


class EmergencyAlert(models.Model):
    LEVEL_CHOICES = [
        ('info', 'Info (Blue)'),
        ('warning', 'Warning (Orange)'),
        ('danger', 'Critical (Red)'),
    ]
    message = models.TextField()
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='danger')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.level.upper()}: {self.message[:50]}"