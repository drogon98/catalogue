# Generated by Django 3.0 on 2020-10-11 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0017_auto_20200927_2054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
