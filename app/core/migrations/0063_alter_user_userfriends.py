# Generated by Django 4.0.10 on 2023-05-24 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0062_user_usercoverpictureurl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='userFriends',
            field=models.IntegerField(default=0),
        ),
    ]
