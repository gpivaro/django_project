# Generated by Django 2.2.13 on 2021-08-24 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airtrafficapp', '0005_auto_20210205_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countrylatlon',
            name='name',
            field=models.CharField(max_length=500),
        ),
    ]