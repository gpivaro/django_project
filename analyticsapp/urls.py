from django.urls import path, include
from . import views

urlpatterns = [
    # path for the index page
    path("", views.index, name="index")
]

