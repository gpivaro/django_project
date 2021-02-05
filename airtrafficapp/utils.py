import os
import json
import requests
from .models import ClientIPAddress

# Import credentials for the API
with open("/etc/config.json") as config_file:
    config = json.load(config_file)

Geo_IPIFY_API = config["Geo_IPIFY_API"]


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
            ipaddress=response["ip"],
            country=response["location"]["country"],
            region=response["location"]["region"],
            city=response["location"]["city"],
            latitude=response["location"]["lat"],
            longitude=response["location"]["lng"],
        )
