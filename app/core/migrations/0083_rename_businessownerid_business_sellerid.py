# Generated by Django 4.0.10 on 2023-09-07 11:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0082_business_businessoperatinglatitude_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='business',
            old_name='businessOwnerId',
            new_name='sellerId',
        ),
    ]