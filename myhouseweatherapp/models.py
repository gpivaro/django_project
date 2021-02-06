from django.db import models


# Class for the weather meas database table
class Weather(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    meas_time = models.DateTimeField(auto_now_add=True)
    sensor = models.IntegerField()
    temperature = models.FloatField()
    humidity = models.FloatField()

    def __str__(self):
        return "<Time: {}, ID: {}, Sensor: {}, temperature: {}, humidity: {}>".format(
            self.meas_time, self.id, self.sensor, self.temperature, self.humidity
        )

    class Meta:
        ordering = ["-meas_time"]


# Class to create the model to save the visitor's ip address
class ClientIPAddress(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    ip_address = models.CharField(max_length=120, blank=True, null=True)
    host_address = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=120, blank=True, null=True)
    region = models.CharField(max_length=120, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self,):
        return "%s viewed: %s" % (self.ip_address, self.timestamp)

    class Meta:
        ordering = ["-timestamp"]
