# Generated by Django 4.0.10 on 2023-03-10 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_rename_phone_num_user_userphonenumber_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='userAccountRegisterDate',
        ),
        migrations.RemoveField(
            model_name='user',
            name='userBio',
        ),
        migrations.RemoveField(
            model_name='user',
            name='userBirthDate',
        ),
        migrations.RemoveField(
            model_name='user',
            name='userPostComment',
        ),
        migrations.RemoveField(
            model_name='user',
            name='userPostCommentView',
        ),
        migrations.RemoveField(
            model_name='user',
            name='userPostDishSellerVisit',
        ),
        migrations.RemoveField(
            model_name='user',
            name='userPostDishVisit',
        ),
        migrations.RemoveField(
            model_name='user',
            name='userPostLike',
        ),
        migrations.RemoveField(
            model_name='user',
            name='userPostSave',
        ),
        migrations.RemoveField(
            model_name='user',
            name='userPostShare',
        ),
        migrations.RemoveField(
            model_name='user',
            name='userPostView',
        ),
        migrations.RemoveField(
            model_name='user',
            name='userProfilePictureUrl',
        ),
    ]
