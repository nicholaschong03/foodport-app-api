# Generated by Django 4.0.10 on 2023-02-18 05:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_alter_user_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
