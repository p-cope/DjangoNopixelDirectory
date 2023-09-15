# Generated by Django 4.2.5 on 2023-09-15 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Directory', '0006_gang_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='streamer',
            name='streamer_title',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='streamer',
            name='streamer_viewcount',
            field=models.IntegerField(default=0),
        ),
    ]