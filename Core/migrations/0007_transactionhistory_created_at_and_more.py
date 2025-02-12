# Generated by Django 5.1.6 on 2025-02-08 22:41

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0006_pixwithdrawal'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionhistory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transactionhistory',
            name='credits',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transactionhistory',
            name='status',
            field=models.CharField(choices=[('Aprovado', 'Aprovado'), ('Pendente', 'Pendente'), ('Recusado', 'Recusado')], default=1, max_length=20),
            preserve_default=False,
        ),
    ]
