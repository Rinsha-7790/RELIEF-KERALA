from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camps', '0007_camp_panchayath'),
    ]

    operations = [
        migrations.AlterField(
            model_name='need',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending Verification'),
                    ('verified', 'Verified'),
                    ('rejected', 'Rejected'),
                ],
                default='verified',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='need',
            name='verified_by_district_officer',
            field=models.BooleanField(default=False),
        ),
    ]