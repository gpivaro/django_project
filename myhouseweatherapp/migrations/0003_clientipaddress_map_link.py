# Generated by Django 2.2.13 on 2021-02-09 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myhouseweatherapp', '0002_auto_20210209_0610'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientipaddress',
            name='map_link',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
