# Generated by Django 4.0.10 on 2023-02-18 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_user_phone_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(default='username', max_length=255),
        ),
    ]
