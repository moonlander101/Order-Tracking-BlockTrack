# Generated by Django 5.2 on 2025-05-17 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier_request', '0003_alter_supplierrequest_unit_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplierrequest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
