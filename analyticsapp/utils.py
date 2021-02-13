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


# Get IP address info. Used as the first option but does not bring accurrate info
def GeoIPIFY(request, ip):

    ip_url = f"https://geo.ipify.org/api/v1?apiKey={Geo_IPIFY_API}&ipAddress={ip}"

    # Get the the ipaddress info from the geo.ipify API
    response = requests.get(ip_url).json()

    # Create a variable for lat and lon
    latitude = response["location"]["lat"]
    longitude = response["location"]["lng"]

    # Create a dictionary with all the info about the client access
    response_dict_GeoIPIFY = {
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

    return response_dict_GeoIPIFY


# Get IP address info. Used as the second option with more accurate
def ipapi(request, ip):

    ip_url = f"http://ip-api.com/json/{ip}"

    # Get the the ipaddress info from the geo.ipify API
    response = requests.get(ip_url).json()

    # Create a variable for lat and lon
    latitude = response["lat"]
    longitude = response["lon"]

    response_dict_ipapi = {
        "ip_address": ip,
        "country": response["country"],
        "region": response["region"],
        "city": response["city"],
        "countryCode": response["countryCode"],
        "regionName": response["regionName"],
        "zip": response["zip"],
        "isp": response["isp"],
        "org": response["org"],
        "asname": response["as"],
        "latitude": latitude,
        "longitude": longitude,
        "map_link": f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map=15/{latitude}/{longitude}",
        "absolute_uri": request.build_absolute_uri(),
        "path": request.path,
        "issecure": request.is_secure(),
        "useragent": request.headers["User-Agent"],
    }

    return response_dict_ipapi


# Get IP address
def get_client_ip(request, Save=False):

    # Define an empty dict to return in case of conditions false
    response_dict = {}

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    # check if the same ip was saved in the last hour
    # verify_ip_last_1h = (
    #     ClientIPAddress.objects.filter(ip_address=ip)
    #     .filter(timestamp__gt=timezone.now() - timedelta(hours=6) + timedelta(hours=1))
    #     .count()
    # )

    # if ip:
    if ip and ip != "127.0.0.1":

        response_dict = ipapi(request, ip)

        # Save the client access data to the database if Save == True
        if Save:
            ClientIPAddress.objects.create(
                ip_address=response_dict["ip_address"],
                country=response_dict["country"],
                region=response_dict["region"],
                city=response_dict["city"],
                countryCode=response_dict["countryCode"],
                regionName=response_dict["regionName"],
                zip=response_dict["zip"],
                isp=response_dict["isp"],
                org=response_dict["org"],
                asname=response_dict["asname"],
                latitude=response_dict["latitude"],
                longitude=response_dict["longitude"],
                map_link=response_dict["map_link"],
                absolute_uri=response_dict["absolute_uri"],
                path=response_dict["path"],
                issecure=response_dict["issecure"],
                useragent=response_dict["useragent"],
            )

    return response_dict

