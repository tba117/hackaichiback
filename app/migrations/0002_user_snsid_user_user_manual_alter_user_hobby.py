# Generated by Django 5.0.2 on 2024-09-22 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='snsid',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='user',
            name='user_manual',
            field=models.TextField(blank=True),
        ),
    ]
