# Generated by Django 4.0.10 on 2023-02-22 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_post_postcomment_post_postcommentview_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='postDishVisit',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
