# Generated by Django 3.0 on 2020-09-21 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_product_prev_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='img_urls',
            field=models.TextField(null=True),
        ),
    ]
