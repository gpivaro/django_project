# Generated by Django 2.2.13 on 2021-02-09 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myhouseweatherapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientipaddress',
            name='absolute_uri',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='clientipaddress',
            name='issecure',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='clientipaddress',
            name='path',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='clientipaddress',
            name='useragent',
            field=models.TextField(null=True),
        ),
    ]
