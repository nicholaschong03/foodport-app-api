# Generated by Django 4.0.10 on 2023-06-11 09:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0068_menuitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='deliciousRating',
            field=models.FloatField(error_messages={'blank': 'Please provide a rating from 1 to 5'}, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='postRatingDelicious',
            field=models.FloatField(error_messages={'blank': 'Please provide a rating from 1 to 5'}, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='worthItRating',
            field=models.FloatField(error_messages={'blank': 'Please provide a rating from 1 to 5'}, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
