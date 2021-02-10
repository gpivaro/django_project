from django.urls import path, include
from . import views

urlpatterns = [
    # path for the index page
    path("", views.index, name="analytics-index"),
    # path to show IP Address or the count of IPs
    path(
        "show-visitors/<str:granularity>/",
        views.show_visitors_ip,
        name="analytics-show-visitors-ip",
    ),
]
