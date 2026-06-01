from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='property_type',
            field=models.CharField(choices=[('apartment', 'Apartment'), ('villa', 'Villa'), ('house', 'House'), ('commercial', 'Commercial'), ('land', 'Land')], default='apartment', max_length=20),
        ),
        migrations.AddField(
            model_name='property',
            name='approval_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='approved', max_length=20),
        ),
        migrations.AddField(
            model_name='property',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
    ]
