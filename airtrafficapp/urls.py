from django.urls import path
from . import views

urlpatterns = [
    # path for the index page
    path("", views.index, name="airtraffic-index"),
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
    path("api-routes", views.api_routes, name="airtraffic-api-routes"),
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
]
