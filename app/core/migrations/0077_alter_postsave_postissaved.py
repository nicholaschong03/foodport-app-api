# Generated by Django 4.0.10 on 2023-08-23 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0076_postsave'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postsave',
            name='postIsSaved',
            field=models.BooleanField(default=False),
        ),
    ]
