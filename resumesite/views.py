from django.shortcuts import render


def home(request):
    return render(request, "resumesite/home.html", {})


def index(request):
    return render(request, "resumesite/index.html", {})


def willcar(request):
    return render(request, "resumesite/willcar.html", {})


def git(request):
    return render(request, "resumesite/git.html", {})
