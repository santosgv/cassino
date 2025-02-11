# Generated by Django 5.1.6 on 2025-02-11 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0009_delete_pixwithdrawal'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transactionhistory',
            options={'verbose_name_plural': 'Historico de transaçoes'},
        ),
        migrations.AlterModelOptions(
            name='usercredit',
            options={'verbose_name_plural': 'Creditos'},
        ),
        migrations.AddField(
            model_name='usercredit',
            name='total_bet',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='usercredit',
            name='total_won',
            field=models.IntegerField(default=0),
        ),
    ]
