# Generated by Django 2.0.7 on 2018-08-27 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxi_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='login',
            field=models.CharField(max_length=20, unique=True, verbose_name='Логін'),
        ),
    ]
