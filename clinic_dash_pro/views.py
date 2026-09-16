# views.py

from django.shortcuts import render


def clinicdashpro_home(request):
    return render(request, "clinic_dash_pro/home.html")
