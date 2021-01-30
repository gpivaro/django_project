from django.shortcuts import render
from django.http import JsonResponse
from .models import Aircrafts, Airports
from .serializers import AircraftsSerializer
from rest_framework import viewsets
from django.db.models import Count


# Main page of the application
def index(request):
    # aircraftdata = Aircrafts.objects.order_by("-time")
    # context = {"aircraftdata": aircraftdata}
    return render(request, "airtrafficapp/index_Gabriel_v4.html")


# Return the info for all aircrafts using rest framework
class AircraftsView(viewsets.ModelViewSet):
    queryset = Aircrafts.objects.exclude(latitude=None).all()
    serializer_class = AircraftsSerializer


# Return the info all aircrafts
def aircrafts(request, country):
    # data = list(Aircrafts.objects.values())

    if country == "ALL":
        # Get the last timestamp
        timestamp = Aircrafts.objects.exclude(latitude=None).latest("time")
        # Query all excluding the latitudes not null
        data = list(
            Aircrafts.objects.exclude(latitude=None)
            .filter(time=timestamp.time)
            .all()
            .values()
        )
    elif country == "byhour":
        data = list(
            Aircrafts.objects.values("time").annotate(totalDataPoints=Count("time"))
        )
    else:
        data = list(
            Aircrafts.objects.exclude(latitude=None)
            .filter(origin_country=country)
            .all()
            .values()
        )

    return JsonResponse(data, safe=False)


# Return the info for one specific CallSign
def callsign(request, CallSign):
    # data = list(Aircrafts.objects.values())
    data = list(
        Aircrafts.objects.exclude(latitude=None)
        .filter(callsign=CallSign)
        .all()
        .values()
    )
    return JsonResponse(data, safe=False)


# Return the info for one specific icao24
def icao24(request, ICAO24):
    # data = list(Aircrafts.objects.values())
    data = list(
        Aircrafts.objects.exclude(latitude=None).filter(icao24=ICAO24).all().values()
    )
    return JsonResponse(data, safe=False)


# Return the info for airports
def airports(request, country):
    if country == "ALL":
        data = list(Airports.objects.all().values())
    else:
        data = list(Airports.objects.filter(Country=country).all().values())

    return JsonResponse(data, safe=False)

