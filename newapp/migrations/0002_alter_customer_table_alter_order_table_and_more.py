# Generated by Django 4.2.7 on 2023-11-22 04:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='customer',
            table='customer',
        ),
        migrations.AlterModelTable(
            name='order',
            table='order',
        ),
        migrations.AlterModelTable(
            name='orderitem',
            table='order_item',
        ),
        migrations.AlterModelTable(
            name='product',
            table='product',
        ),
        migrations.AlterModelTable(
            name='shippingaddress',
            table='shipping_address',
        ),
    ]