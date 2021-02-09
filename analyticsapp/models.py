from django.db import models


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
