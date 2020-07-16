from django.shortcuts import render


def dashboard(requests):
    return render(requests, "dashboard/welcome.html")
