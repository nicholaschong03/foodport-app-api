# Generated by Django 4.0.10 on 2023-09-07 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0083_rename_businessownerid_business_sellerid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menuitem',
            old_name='name',
            new_name='menuName',
        ),
    ]
