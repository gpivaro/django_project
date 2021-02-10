from django.shortcuts import render
from analyticsapp.utils import get_client_ip


def home(request):
    get_client_ip(request, True)
    return render(request, "resumesite/home.html", {})


def git(request):
    get_client_ip(request, True)
    return render(request, "resumesite/git.html", {})

