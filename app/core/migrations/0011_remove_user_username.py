# Generated by Django 4.0.10 on 2023-02-17 11:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_user_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
