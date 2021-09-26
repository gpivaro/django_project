from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import Weather, ClientIPAddress
from .utils import weather_api
from datetime import datetime, timedelta
from django.utils import timezone
from analyticsapp.utils import get_client_ip
from django.views.generic import ListView
from django.db.models import Count, Min, Max, Avg, F, RowRange, Window

# Number of sensor active
num_sensor = 2


# Main page of the application
def index(request):
    get_client_ip(request, True)
    data = weather_api("Houston")
    return render(request, "myhouseweatherapp/index.html", {"data": data})


class DataMeasView(ListView):
    model = Weather
    paginate_by = num_sensor * 60 * 24  # To get data for the last 24h
    # queryset = Weather.objects.filter(temperature__gte=25)
    # queryset = Weather.objects.values_list("temperature", flat=True)

    # Customazing the results
    # def get_queryset(self):
    # return Weather.objects.filter(temperature__gte=25)
    # return Weather.objects.filter(temperature__gte=25)


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


# Return json data of last x hours
def weather_data_moving_average(request, last_hours):

    # Note that the APP is using UTC time zone.
    data = list(
        Weather.objects.annotate(
            temperature_moving_avg=Window(
                expression=Avg("temperature"),
                partition_by=[F("sensor_name")],
                order_by=F("meas_time").asc(),
                frame=RowRange(start=-5, end=0),
            )
        )
        .filter(
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
        f"<h3><a href ='/homeweather'>Home Weather</a> | API endpoints: </h3>"
        f"<li>api/v1.0/weather-data/last_hours/&nbsp</li>"
        f"<ul><li>Example: <a href ='api/v1.0/weather-data/1/'>Last 1h measurements</a></li></ul>"
        f"<ul><li>Example: <a href ='api/v1.0/weather-data/24/'>Last 24h measurements</a></li></ul>"
        f"<li>api/v1.0/weather-data-moving-average/</li>"
        f"<ul><li>Example: <a href ='api/v1.0/weather-data-moving-average/1/'>Last 1h measurements</a></li></ul>"
        f"<li>api/v1.0/weather-api/city/ &nbsp </li>"
        f"<ul><li>Example: <a href ='api/v1.0/weather-api/Houston/'>Houston, Tx weather</a></li></ul>"
    )


# from myhouseweatherapp.models import Weather
# from datetime import datetime, timedelta
# from django.utils import timezone
# Weather.objects.filter(meas_time__gt=timezone.now() - timedelta(hours=6)).count()


# Working with Django Annotate (Window Functions):
# from django.db.models import Count, Min, Max, Avg, F, RowRange, Window
# weather = Weather.objects.all().first()
# weather[0]
# vars(weather[0])
# min_temperature = Weather.objects.annotate(Min('temperature'))
# min_temperature

# https://stackoverflow.com/questions/48790322/fast-moving-average-computation-with-django-orm
# https://docs.djangoproject.com/en/3.1/ref/models/expressions/#django.db.models.expressions.Window

# weather = Weather.objects.annotate(
#     moving_avg_temperature=Window(
#         expression=Avg('temperature'),
#         partition_by=[F('sensor_name')],
#         order_by=F('meas_time').asc(),
#         frame=RowRange(start=-5,end=0)
#     )
# ).filter(meas_time__gt=timezone.now() - timedelta(hours=6))
# vars(weather[0])


# data = list(
#     Weather.objects.annotate(
#         moving_avg_temperature=Window(
#             expression=Avg("temperature"),
#             partition_by=[F("sensor_name")],
#             order_by=F("meas_time").desc(),
#             frame=RowRange(start=-5, end=0),
#         )
#     )
# )

# data[0].moving_avg_temperature
