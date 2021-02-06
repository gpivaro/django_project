from django.urls import path, include
from . import views
from rest_framework import routers
from .views import AircraftsView

# router = routers.DefaultRouter()
# router.register("aircrafts", views.AircraftsView)

urlpatterns = [
    # path for the index page
    path("", views.index, name="index"),
    # path for: /api/v1.0/aircrafts-data/ALL   /api/v1.0/aircrafts-data/Brazil
    path("api/v1.0/aircrafts-data/<country>/", views.aircrafts, name="aircrafts"),
    # path for icao24
    path("api/v1.0/aircrafts-data/icao24/<ICAO24>/", views.icao24, name="icao24"),
    # path for callsign
    path(
        "api/v1.0/aircrafts-data/callsign/<CallSign>/", views.callsign, name="callsign"
    ),
    path("api/v1.0/airports-data/<country>/", views.airports, name="airports"),
    # Delete entries
    path("api/v1.0/aircrafts-delete", views.aircrafts_delete, name="aircrafts_delete"),
    # API routes
    path("api-routes", views.api_routes, name="api_routes"),
    # Return Country coordinates
    path(
        "api/v1.0/country-coordinates/<country>/",
        views.country_coordinates,
        name="country_coordinates",
    ),
    # Show IP Address or the count of IPs
    path(
        "analytics/show-visitors/<granularity>/",
        views.show_visitors_ip,
        name="show_visitors_ip",
    ),
    # Using Rest Framework
    # path("api/v1.0/aircrafts-data/<Country>/", include(router.urls)),
    # path("api/v1.0/aircrafts-data/<username>/", AircraftsView.as_view()),
]
