# Generated by Django 4.0.10 on 2023-04-28 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0054_remove_seller_dishid'),
    ]

    operations = [
        migrations.AddField(
            model_name='seller',
            name='dishId',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
