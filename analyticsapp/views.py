from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .utils import get_client_ip
from .models import ClientIPAddress

# Create your views here.
def index(request):
    client_access_info = get_client_ip(request, False)
    # return HttpResponse("Hello, welcome to analytics!")
    return JsonResponse(client_access_info, safe=False)


# Show all visitors' IP address
def show_visitors_ip(request, granularity):

    if granularity == "all":
        data = list(ClientIPAddress.objects.all().values())
    elif granularity == "count":
        data = {"visits": ClientIPAddress.objects.count()}

    return JsonResponse(data, safe=False)
