# Generated by Django 4.0.10 on 2023-09-22 06:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0080_postshare'),
    ]

    operations = [
        migrations.RenameField(
            model_name='postcomment',
            old_name='comment',
            new_name='commentContent',
        ),
        migrations.RenameField(
            model_name='postcomment',
            old_name='commentDateTime',
            new_name='commentPublishDateTime',
        ),
        migrations.RenameField(
            model_name='postcomment',
            old_name='commentIpAddress',
            new_name='commentPublishIpAddress',
        ),
        migrations.RemoveField(
            model_name='menuitem',
            name='postId',
        ),
        migrations.RemoveField(
            model_name='menuitem',
            name='totalPostCount',
        ),
        migrations.RemoveField(
            model_name='post',
            name='menuItemId',
        ),
        migrations.AddField(
            model_name='post',
            name='menuItem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='core.menuitem'),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='commentLikeCount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='commentLikes',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='commentPublishLastUpdatedDateTime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='commentPublishLocation',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='commentReplies',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='userLatitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='userLongitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isActive', models.BooleanField(default=True)),
                ('likeDateTime', models.DateTimeField(auto_now_add=True)),
                ('likeIpAddress', models.GenericIPAddressField(blank=True, null=True)),
                ('likeUserAgent', models.TextField(blank=True, null=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='core.postcomment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_likes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('businessName', models.CharField(max_length=255)),
                ('businessOperatingLocation', models.JSONField(blank=True, null=True)),
                ('businessOperatingTime', models.JSONField(blank=True, null=True)),
                ('businessVerified', models.BooleanField(default=False)),
                ('businessSafeFood', models.BooleanField(default=False)),
                ('businessHalal', models.BooleanField(default=False)),
                ('sellerId', models.IntegerField(blank=True, null=True)),
                ('businessInfoContributor', models.JSONField(blank=True, null=True)),
                ('businessOperatingLatitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('businessOperatingLongitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('businessTrendRanking', models.IntegerField(blank=True, null=True)),
                ('followers', models.ManyToManyField(blank=True, related_name='following_businesses', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='menuitem',
            name='business',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='core.business'),
        ),
    ]