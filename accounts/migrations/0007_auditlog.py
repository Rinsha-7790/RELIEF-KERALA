from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_customuser_approved_by_field_officer_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('login', 'Login'), ('logout', 'Logout'), ('register', 'Registration'), ('approve_staff', 'Staff Approved'), ('reject_staff', 'Staff Rejected'), ('approve_volunteer', 'Volunteer Approved'), ('allocate_funds', 'Funds Allocated'), ('add_camp', 'Camp Added'), ('update_camp', 'Camp Updated'), ('add_need', 'Need Reported'), ('verify_need', 'Need Verified'), ('donate_money', 'Money Donated'), ('donate_item', 'Item Donated'), ('update_delivery', 'Delivery Updated'), ('emergency_alert', 'Emergency Alert Issued'), ('other', 'Other')], max_length=30)),
                ('description', models.TextField()),
                ('target_user', models.CharField(blank=True, help_text='Username of the affected user, if any', max_length=150)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('extra_data', models.JSONField(blank=True, help_text='Any additional structured info', null=True)),
                ('performed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]