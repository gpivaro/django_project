from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import Aircrafts, Airports, CountryLatLon
from .serializers import AircraftsSerializer
from rest_framework import viewsets
from django.db.models import Count
from datetime import datetime, timedelta

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
        # Get the last timestamp
        timestamp = Aircrafts.objects.exclude(latitude=None).latest("time")
        data = list(
            Aircrafts.objects.exclude(latitude=None)
            .filter(time=timestamp.time)
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


# Return the coordinates of the country
def country_coordinates(request, country):
    data = list(CountryLatLon.objects.filter(name=country).all().values())
    return JsonResponse(data, safe=False)


# Clear old entries on the aircraft table
def aircrafts_delete(request):

    current_records = Aircrafts.objects.count()
    timestamp_7days = round(datetime.timestamp(datetime.now() - timedelta(days=7)))
    records_old_7days = Aircrafts.objects.filter(time__lt=timestamp_7days).count()
    Aircrafts.objects.filter(time__lte=timestamp_7days).delete()
    return HttpResponse(
        f"Records deleted: {records_old_7days} | Current records on db: {current_records}<br/>"
        f"<p><a href='/'>Home</a></p>"
    )


# Return the APIs route available
def api_routes(request):

    return HttpResponse(
        f"<h3>API end points available:</h3>"
        f"/api/v1.0/aircrafts-data/<br/>"
        f"/api/v1.0/airports-data/enter_country_name<br/>"
        f"/api/v1.0/aircrafts-data/icao24/enter_icao24<br/>"
        f"/api/v1.0/aircrafts-data/callsign/enter_callsign<br/>"
        f"/api/v1.0/aircrafts-data/byhour<br/>"
        f"/api/v1.0/country-coordinates/enter_country_name<br/>"
        f"/api/v1.0/aircrafts-delete"
    )
