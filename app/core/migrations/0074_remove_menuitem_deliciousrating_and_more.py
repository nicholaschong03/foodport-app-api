# Generated by Django 4.0.10 on 2023-06-12 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0073_rename_dishid_seller_menuitemid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menuitem',
            name='deliciousRating',
        ),
        migrations.RemoveField(
            model_name='menuitem',
            name='eatAgainRating',
        ),
        migrations.RemoveField(
            model_name='menuitem',
            name='worthItRating',
        ),
    ]
