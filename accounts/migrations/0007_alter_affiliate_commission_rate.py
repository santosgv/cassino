# Generated by Django 5.1.6 on 2025-02-08 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_delete_usuarios'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliate',
            name='commission_rate',
            field=models.DecimalField(decimal_places=2, default=5, max_digits=5),
        ),
    ]
