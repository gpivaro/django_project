from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("index/", views.index, name="index"),
    path("willcar/", views.willcar, name="willcar"),
    path("git/", views.git, name="git"),
]
