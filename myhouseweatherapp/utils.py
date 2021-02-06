import os
import json
import requests
from datetime import datetime, timedelta
from .models import ClientIPAddress

# Import credentials for the API
with open("/etc/config.json") as config_file:
    config = json.load(config_file)

Geo_IPIFY_API = config["Geo_IPIFY_API"]
weather_api_key = config["OPENWEATHERMAP_API_KEY"]

# Get IP address
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    if ip and ip != "127.0.0.1":
        ip_url = f"https://geo.ipify.org/api/v1?apiKey={Geo_IPIFY_API}&ipAddress={ip}"
        response = requests.get(ip_url).json()

        ClientIPAddress.objects.create(
            ip_address=response["ip"],
            host_address=request.headers["Host"],
            country=response["location"]["country"],
            region=response["location"]["region"],
            city=response["location"]["city"],
            latitude=response["location"]["lat"],
            longitude=response["location"]["lng"],
        )


# openweather API for weather data
def weather_api(city):
    # Save config information.
    url = "http://api.openweathermap.org/data/2.5/weather?"
    units = "imperial"

    # Build partial query URL
    query_url = f"{url}appid={weather_api_key}&units={units}&q="

    print(query_url + city)

    response = requests.get(query_url + city).json()

    return {
        "temp": response["main"]["temp"],
        "temp_min": response["main"]["temp_min"],
        "temp_max": response["main"]["temp_max"],
        "feels_like": response["main"]["feels_like"],
        "weather_main": response["weather"][0]["main"],
        "weather_description": response["weather"][0]["description"],
        "clouds": response["clouds"]["all"],
        "wind_speed": response["wind"]["speed"],
        "humidity": response["main"]["humidity"],
        "pressure": response["main"]["pressure"],
        "visibility": response["visibility"],
        "icon_url": f"http://openweathermap.org/img/wn/{response['weather'][0]['icon']}@2x.png",
        "sunrise": datetime.utcfromtimestamp(response["sys"]["sunrise"])
        - timedelta(hours=6),
        "sunset": datetime.utcfromtimestamp(response["sys"]["sunset"])
        - timedelta(hours=6),
        "meastime": datetime.utcfromtimestamp(response["dt"]) - timedelta(hours=6),
    }


# OpenAQ API for air quality
def airquality():
    # Air quality for Houston East
    airquality_url = "https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com/v2/latest?limit=100&page=1&offset=0&sort=desc&radius=1000&country=US&city=Houston&location=Houston%20East%20C1%2FG316&order_by=lastUpdated&dumpRaw=false"

    response = requests.get(airquality_url).json()
