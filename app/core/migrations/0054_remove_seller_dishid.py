# Generated by Django 4.0.10 on 2023-04-28 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_alter_seller_dishid_alter_seller_sellerownerid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seller',
            name='dishId',
        ),
    ]
