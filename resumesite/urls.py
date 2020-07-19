from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="resumesite-home"),
    path("git/", views.git, name="resumesite-git"),
    path("index/", views.index, name="resumesite-home-index"),
]
