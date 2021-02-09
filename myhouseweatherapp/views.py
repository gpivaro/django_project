from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import Weather, ClientIPAddress
from .utils import get_client_ip, weather_api
from datetime import datetime, timedelta
from django.utils import timezone


# Main page of the application
def index(request):
    get_client_ip(request)
    data = weather_api("Houston")
    return render(request, "myhouseweatherapp/index.html", {"data": data})


# Return json data of last x hours
def weather_data(request, last_hours):
    # data = list(Weather.objects.order_by("-meas_time").all().values())

    # Note that the APP is using UTC time zone.
    data = list(
        Weather.objects.filter(
            meas_time__gt=timezone.now()
            - timedelta(hours=6)
            - timedelta(hours=last_hours)
        )
        .all()
        .values()
    )

    return JsonResponse(data, safe=False)


# Show all visitors' IP address
def show_visitors_ip(request, granularity):

    if granularity == "all":
        data = list(ClientIPAddress.objects.all().values())
    elif granularity == "count":
        data = {"visits": ClientIPAddress.objects.count()}

    return JsonResponse(data, safe=False)


# Get data from the Openweathermap API
def get_weather_api_data(request, city):
    data = weather_api(city)
    return JsonResponse(data, safe=False)


# Return the APIs route available
def api_routes(request):

    return HttpResponse(
        f"<h3>API end points available:</h3>"
        f"api/v1.0/weather-data/last_hours/<br/>"
        f"api/v1.0/weather-api/city/<br/><br/>"
        f"<a href ='/houseweather'>Home</a>"
    )


# from myhouseweatherapp.models import Weather
# from datetime import datetime, timedelta
# from django.utils import timezone
# Weather.objects.filter(meas_time__gt=timezone.now() + timedelta(hours=1)).count()


# from myhouseweatherapp.models import ClientIPAddress
# from datetime import datetime, timedelta
# from django.utils import timezone
# ClientIPAddress.objects.all().values()
# ClientIPAddress.objects.filter(timestamp__gt=timezone.now() + timedelta(hours=1)).all().values()


# ClientIPAddress.objects.filter(ip_address='127.0.0.1').delete()
# ClientIPAddress.objects.filter(ip_address='107.128.116.227').delete()
