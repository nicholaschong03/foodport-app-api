# Generated by Django 4.0.10 on 2023-05-15 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_user_usergender_alter_post_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='userLocation',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
