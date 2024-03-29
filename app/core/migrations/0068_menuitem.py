# Generated by Django 4.0.10 on 2023-06-11 07:26

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0067_remove_post_postlike_postlike'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('postId', models.JSONField(blank=True, default=list, null=True)),
                ('dishInfoContributor', models.JSONField(blank=True, default=dict, null=True)),
                ('sellerId', models.IntegerField(blank=True, null=True)),
                ('category', models.CharField(max_length=255)),
                ('basicIngredient', models.JSONField(blank=True, default=list, null=True)),
                ('compositeIngredient', models.JSONField(blank=True, default=list, null=True)),
                ('nutritionFacts', models.JSONField(blank=True, default=dict, null=True)),
                ('totalPostCount', models.IntegerField(default=0)),
                ('postRatingDelicious', models.FloatField(error_messages={'blank': 'Please provide a rating from 1 to 5'}, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('deliciousRating', models.FloatField(error_messages={'blank': 'Please provide a rating from 1 to 5'}, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('worthItRating', models.FloatField(error_messages={'blank': 'Please provide a rating from 1 to 5'}, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('trendingPosition', models.IntegerField(blank=True, null=True)),
                ('trendingDirection', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
