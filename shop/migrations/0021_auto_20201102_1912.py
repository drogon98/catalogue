# Generated by Django 3.0 on 2020-11-02 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0020_auto_20201101_1849'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cart_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='currency',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='currency_value',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Product'),
        ),
        migrations.DeleteModel(
            name='Query',
        ),
    ]
