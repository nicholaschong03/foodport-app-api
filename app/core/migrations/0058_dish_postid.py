# Generated by Django 4.0.10 on 2023-05-10 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0057_remove_dish_postid'),
    ]

    operations = [
        migrations.AddField(
            model_name='dish',
            name='postId',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
