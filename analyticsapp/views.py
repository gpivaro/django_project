from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .utils import get_client_ip
from .models import ClientIPAddress


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

