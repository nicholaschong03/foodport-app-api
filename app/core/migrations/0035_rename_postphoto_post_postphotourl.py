# Generated by Django 4.0.10 on 2023-03-08 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_rename_postphotourl_post_postphoto'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='postPhoto',
            new_name='postPhotoUrl',
        ),
    ]