# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.clinicdashpro_home, name='clinicdashpro_home'),
]
