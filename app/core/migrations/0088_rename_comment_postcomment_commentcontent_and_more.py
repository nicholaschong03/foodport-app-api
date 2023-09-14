# Generated by Django 4.0.10 on 2023-09-14 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0087_menuitem_sellerid'),
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
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='commentReplises',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]