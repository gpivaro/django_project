from django.db import models


# Class to create the model to save the visitor's ip address
class ClientIPAddress(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    ip_address = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=120, blank=True, null=True)
    region = models.CharField(max_length=120, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    countryCode = models.CharField(max_length=120, blank=True, null=True)
    regionName = models.CharField(max_length=120, blank=True, null=True)
    zip = models.CharField(max_length=120, blank=True, null=True)
    isp = models.TextField(null=True)
    org = models.TextField(null=True)
    asname = models.TextField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    map_link = models.TextField(null=True)
    absolute_uri = models.CharField(max_length=300, blank=True, null=True)
    path = models.CharField(max_length=200, blank=True, null=True)
    issecure = models.BooleanField(null=True)
    useragent = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self,):
        return "%s | %s | %s | %s | %s " % (
            self.ip_address,
            self.path,
            self.country,
            self.city,
            self.timestamp,
        )

    class Meta:
        ordering = ["-timestamp"]


# from analyticsapp.models import ClientIPAddress
# from datetime import datetime, timedelta
# from django.utils import timezone
# ClientIPAddress.objects.all().values()
# ClientIPAddress.objects.filter(timestamp__gt=timezone.now() + timedelta(hours=1)).all().values()


# ClientIPAddress.objects.filter(ip_address='127.0.0.1').delete()
# ClientIPAddress.objects.filter(ip_address='107.128.116.227').delete()
