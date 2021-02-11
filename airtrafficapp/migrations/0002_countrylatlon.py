# Generated by Django 2.2.13 on 2021-02-03 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airtrafficapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountryLatLon',
            fields=[
                ('countryID', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='CountryID')),
                ('country', models.CharField(max_length=3)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]