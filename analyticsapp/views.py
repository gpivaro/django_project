from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .utils import get_client_ip

# Create your views here.
def index(request):
    client_access_info = get_client_ip(request, False)
    # return HttpResponse("Hello, welcome to analytics!")
    return JsonResponse(client_access_info, safe=False)
