# Generated by Django 4.0.10 on 2023-09-07 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0084_rename_name_menuitem_menuname'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menuitem',
            old_name='menuName',
            new_name='name',
        ),
    ]
