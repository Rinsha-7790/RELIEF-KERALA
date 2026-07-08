from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('camps', '0006_need_verified_by_field_officer_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='camp',
            name='panchayath',
            field=models.ForeignKey(
                blank=True,
                help_text='Panchayath officer responsible for verifying needs at this camp',
                limit_choices_to={'role': 'panchayath_staff'},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='managed_camps',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]