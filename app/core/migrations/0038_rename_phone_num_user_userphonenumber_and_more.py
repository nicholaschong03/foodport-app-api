# Generated by Django 4.0.10 on 2023-03-10 07:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_remove_post_userid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='phone_num',
            new_name='userPhoneNumber',
        ),
        migrations.AddField(
            model_name='user',
            name='userAccountRegisterDate',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='userBio',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='userBirthDate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='userPostComment',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='user',
            name='userPostCommentView',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='user',
            name='userPostDishSellerVisit',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='user',
            name='userPostDishVisit',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='user',
            name='userPostLike',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='user',
            name='userPostSave',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='user',
            name='userPostShare',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='user',
            name='userPostView',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='user',
            name='userProfilePictureUrl',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]
