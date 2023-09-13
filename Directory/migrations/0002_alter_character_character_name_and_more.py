# Generated by Django 4.2.5 on 2023-09-12 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Directory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='character_name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='streamer',
            name='streamer_name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]