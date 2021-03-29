from django.urls import path, include
from . import views
from .views import IPAccessView, AccessDetailView

app_name = "analyticsapp"
urlpatterns = [
    # path for the index page
    path("my-ip-info/", views.index, name="analytics-index"),
    # path to show IP Address or the count of IPs
    path(
        "show-visitors/<str:granularity>/",
        views.show_visitors_ip,
        name="analytics-show-visitors-ip",
    ),
    # path to export the visitors data as csv
    path("visitors-export-csv/", views.export_csv, name="analytics-export-csv"),
    # path to access stats
    path("website-access-stats/", IPAccessView.as_view(), name="website-access-stats"),
    # path to detail view of one access
    path("access-detail/<int:pk>/", AccessDetailView.as_view(), name="access-detail"),
]
