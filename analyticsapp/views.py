from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .utils import get_client_ip
from .models import ClientIPAddress
from django.views.generic import ListView, DetailView
import csv


# Create your views here.
def index(request):
    client_access_info = get_client_ip(request, False)
    context = {"client_access_info": client_access_info}
    return render(request, "analyticsapp/view-my-ip.html", context)
    # return JsonResponse(client_access_info, safe=False)


# Show all visitors' IP address
def show_visitors_ip(request, granularity):

    # show details about all visitors
    if granularity == "all":
        data = list(ClientIPAddress.objects.all().values())
    # count all visitors in total
    elif granularity == "count":
        data = {"visits": ClientIPAddress.objects.count()}
    # count visitors based on the path
    else:
        data = {
            "visits": ClientIPAddress.objects.filter(
                path__contains=f"{granularity}"
            ).count()
        }
    return JsonResponse(data, safe=False)


# View to export visitors info as CSV file
def export_csv(request):
    response = HttpResponse(content_type="text/csv")

    writer = csv.writer(response)
    writer.writerow(
        [
            "id",
            "ip_address",
            "country",
            "region",
            "city",
            "countryCode",
            "regionName",
            "zip",
            "isp",
            "org",
            "asname",
            "latitude",
            "longitude",
            "map_link",
            "absolute_uri",
            "path",
            "issecure",
            "useragent",
            "timestamp",
        ]
    )

    for ipAddressData in ClientIPAddress.objects.all().values_list(
        "id",
        "ip_address",
        "country",
        "region",
        "city",
        "countryCode",
        "regionName",
        "zip",
        "isp",
        "org",
        "asname",
        "latitude",
        "longitude",
        "map_link",
        "absolute_uri",
        "path",
        "issecure",
        "useragent",
        "timestamp",
    ):
        writer.writerow(ipAddressData)

    response["Content-Disposition"] = 'attachment; filename="ip-data.csv"'

    return response


# List view to see all the access
class IPAccessView(ListView):
    model = ClientIPAddress

    # Access method to retrieve the request ip address
    def get_queryset(self, **kwargs):
        get_client_ip(self.request, Save=True)
        return ClientIPAddress.objects.all()


# Detail view to see individual access
class AccessDetailView(DetailView):
    model = ClientIPAddress

    # Access method to retrieve the request ip address
    def get_queryset(self, **kwargs):
        get_client_ip(self.request, Save=True)
        return ClientIPAddress.objects.all()
