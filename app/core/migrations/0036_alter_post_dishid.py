# Generated by Django 4.0.10 on 2023-03-08 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_rename_postphoto_post_postphotourl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='dishId',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]