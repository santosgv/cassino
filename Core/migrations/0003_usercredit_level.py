# Generated by Django 5.1.6 on 2025-02-07 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0002_usercredit_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercredit',
            name='level',
            field=models.IntegerField(default=1),
        ),
    ]
