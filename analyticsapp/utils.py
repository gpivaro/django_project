import os
import json
import requests
from datetime import datetime, timedelta
from .models import ClientIPAddress
from django.utils import timezone

# Import credentials for the API
with open("/etc/config.json") as config_file:
    config = json.load(config_file)

Geo_IPIFY_API = config["Geo_IPIFY_API"]
weather_api_key = config["OPENWEATHERMAP_API_KEY"]

# Get IP address
def get_client_ip(request, Save=False):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    # check if the same ip was saved in the last hour
    verify_ip_last_1h = (
        ClientIPAddress.objects.filter(ip_address=ip)
        .filter(timestamp__gt=timezone.now() - timedelta(hours=6) + timedelta(hours=1))
        .count()
    )

    # only add visitor if not active in the last hour
    if verify_ip_last_1h == 0:

        if ip:
            # if ip and ip != "127.0.0.1":
            ip_url = (
                f"https://geo.ipify.org/api/v1?apiKey={Geo_IPIFY_API}&ipAddress={ip}"
            )
            # Get the the ipaddress info from the geo.ipify API
            response = requests.get(ip_url).json()

            # Create a variable for lat and lon
            latitude = response["location"]["lat"]
            longitude = response["location"]["lng"]

            # Create a dictionary with all the info about the client access
            response_dict = {
                "ip_address": response["ip"],
                "country": response["location"]["country"],
                "region": response["location"]["region"],
                "city": response["location"]["city"],
                "latitude": latitude,
                "longitude": longitude,
                "map_link": f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map=15/{latitude}/{longitude}",
                "absolute_uri": request.build_absolute_uri(),
                "path": request.path,
                "issecure": request.is_secure(),
                "useragent": request.headers["User-Agent"],
            }

            # Save the client access data to the database if Save == True
            if Save:
                ClientIPAddress.objects.create(
                    ip_address=response_dict["ip_address"],
                    country=response_dict["country"],
                    region=response_dict["region"],
                    city=response_dict["city"],
                    latitude=response_dict["latitude"],
                    longitude=response_dict["longitude"],
                    map_link=response_dict["map_link"],
                    absolute_uri=response_dict["absolute_uri"],
                    path=response_dict["path"],
                    issecure=response_dict["issecure"],
                    useragent=response_dict["useragent"],
                )

    # print(f"Requested uri: {request.build_absolute_uri()}")
    # print(f"Full path to the requested page: {request.path}")
    # print(f"Request is secure: {request.is_secure()}")
    # print(f"User-Agent: {request.headers['User-Agent']}")

    return response_dict

