# Generated by Django 5.0.2 on 2024-09-24 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_user_current_match'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='advice',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
