# Generated by Django 4.0.10 on 2023-04-28 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0055_seller_dishid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seller',
            name='dishId',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
