from django.urls import path, include
from . import views

urlpatterns = [
    # path to the home page of the resume app
    path("", views.home, name="resumesite-home"),
    # path to the git page of the resume app
    path("git/", views.git, name="resumesite-git"),
    path("robots.txt", views.robots, name="resumesite-robots"),
]
