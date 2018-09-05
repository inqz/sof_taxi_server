# Generated by Django 2.0.7 on 2018-09-05 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxi_app', '0003_auto_20180827_1136'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='settings',
            options={'verbose_name': 'налаштування', 'verbose_name_plural': 'Налаштування'},
        ),
        migrations.RemoveField(
            model_name='client',
            name='login',
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('new', 'Нове замовлення'), ('accepted', 'Водій прийняв замовлення'), ('arrived', 'Водій прибув до клієнта'), ('executing', 'Замовлення виконується'), ('finished', 'Замовлення виконане'), ('canceled', 'Замовлення скасовано'), ('payed', 'Замовлення виконано і оплачено')], default='new', max_length=20),
        ),
    ]
