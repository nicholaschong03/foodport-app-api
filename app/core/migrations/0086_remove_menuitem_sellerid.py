# Generated by Django 4.0.10 on 2023-09-08 03:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0085_rename_menuname_menuitem_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menuitem',
            name='sellerId',
        ),
    ]
