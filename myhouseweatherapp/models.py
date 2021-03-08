from django.db import models


# Class for the weather meas database table
class Weather(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    meas_time = models.DateTimeField(auto_now_add=True)
    sensor = models.IntegerField()
    sensor_name = models.CharField(max_length=55, default="Unknown")
    temperature = models.FloatField()
    humidity = models.FloatField()

    def __str__(self):
        return "<Time: {}, Sensor: {}, Location: {}, temperature: {}>".format(
            self.meas_time, self.sensor, self.sensor_name, self.temperature
        )

    class Meta:
        ordering = ["-meas_time"]


## Example of query for the model Weather using shell
# from myhouseweatherapp.models import Weather
# Weather.objects.all()
# weather = Weather.objects.all().first()
# weather.sensor_name
# Weather.objects.filter(sensor_name='Pi0W-Kitchen').all()


# Class to create the model to save the visitor's ip address
class ClientIPAddress(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    ip_address = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=120, blank=True, null=True)
    region = models.CharField(max_length=120, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    map_link = models.TextField(null=True)
    absolute_uri = models.CharField(max_length=300, blank=True, null=True)
    path = models.CharField(max_length=200, blank=True, null=True)
    issecure = models.BooleanField(null=True)
    useragent = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self,):
        return "%s viewed: %s" % (self.ip_address, self.timestamp)

    class Meta:
        ordering = ["-timestamp"]
