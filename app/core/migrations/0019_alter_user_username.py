# Generated by Django 4.0.10 on 2023-02-18 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
