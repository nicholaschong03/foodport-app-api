# Generated by Django 4.0.10 on 2023-03-24 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_dish_dishinfocontributor_dish_dishmainingredient_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='userAge',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='userFollowers',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='userFollowing',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='userFriends',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='userLikes',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='userLocation',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
