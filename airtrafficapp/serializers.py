from rest_framework import serializers
from .models import Aircrafts, Airports


class AircraftsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircrafts
        fields = ("id", "icao24")

