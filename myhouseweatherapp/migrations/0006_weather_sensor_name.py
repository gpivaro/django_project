# Generated by Django 2.2.13 on 2021-03-08 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myhouseweatherapp', '0005_auto_20210209_0651'),
    ]

    operations = [
        migrations.AddField(
            model_name='weather',
            name='sensor_name',
            field=models.CharField(default='Unknown', max_length=55),
        ),
    ]
