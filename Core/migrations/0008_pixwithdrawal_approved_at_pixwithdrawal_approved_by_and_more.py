# Generated by Django 5.1.6 on 2025-02-09 15:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0007_transactionhistory_created_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='pixwithdrawal',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pixwithdrawal',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_withdrawals', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pixwithdrawal',
            name='status',
            field=models.CharField(choices=[('pending', 'Aguardando Aprovação'), ('approved', 'Aprovado'), ('rejected', 'Rejeitado'), ('paid', 'Pago')], default='pending', max_length=20),
        ),
    ]
