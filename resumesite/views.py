from django.shortcuts import render
from analyticsapp.utils import get_client_ip
from django.http import HttpResponse


def home(request):
    get_client_ip(request, True)
    return render(request, "resumesite/home.html", {})


def git(request):
    get_client_ip(request, True)
    return render(request, "resumesite/git.html", {})


def robots(request):
    get_client_ip(request, True)
    filename = "robots.txt"
    content = f"""User-agent: Googlebot \nDisallow: / \n\nUser-agent: PetalBot \nDisallow: / \n\nUser-agent: SemrushBot \nDisallow: /"""
    response = HttpResponse(content, content_type="text/plain")
    # response["Content-Disposition"] = "attachment; filename={0}".format(filename)
    return response

