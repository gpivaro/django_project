from django.db import models

# Class for the aircrafts database table
class Aircrafts(models.Model):
    icao24 = models.CharField(max_length=20)
    callsign = models.CharField(max_length=20)
    origin_country = models.CharField(max_length=50)
    time_position = models.IntegerField()
    last_contact = models.IntegerField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    baro_altitude = models.FloatField()
    on_ground = models.BooleanField()
    velocity = models.FloatField()
    true_track = models.FloatField()
    vertical_rate = models.FloatField()
    sensors = models.CharField(max_length=20)
    geo_altitude = models.FloatField()
    squawk = models.CharField(max_length=20)
    spi = models.BooleanField()
    position_source = models.IntegerField()
    time = models.IntegerField()

    def __str__(self):
        return "<Time: {}, ID: {}, ICAO24: {}>".format(self.time, self.id, self.icao24)


# Class for the airports database table
class Airports(models.Model):
    AirportID = models.AutoField(
        auto_created=True, primary_key=True, serialize=False, verbose_name="AirportID",
    )
    Name = models.CharField(max_length=100)
    City = models.CharField(max_length=100)
    Country = models.CharField(max_length=70)
    IATA = models.CharField(max_length=70)
    ICAO = models.CharField(max_length=70)
    Latitude = models.FloatField()
    Longitude = models.FloatField()
    Altitude = models.FloatField()
    Timezone = models.CharField(max_length=70)
    DST = models.CharField(max_length=70)
    Tzdatabasetimezone = models.CharField(max_length=70)
    Type = models.CharField(max_length=70)
    Source = models.CharField(max_length=70)

    def __str__(self):
        return "<Name: {}, ID: {}, City: {}>".format(
            self.Name, self.AirportID, self.City
        )


# Class for the Country coordinates
class CountryLatLon(models.Model):
    country = models.CharField(max_length=3, primary_key=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return "<Name: {}, ID: {}, City: {}>".format(
            self.name, self.countryID, self.country
        )


# Class to create the model to save the visitor's ip address
class ClientIPAddress(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    ip_address = models.CharField(max_length=120, blank=True, null=True)
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

