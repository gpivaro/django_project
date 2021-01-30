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
    # Using Rest Framework
    # path("api/v1.0/aircrafts-data/<Country>/", include(router.urls)),
    # path("api/v1.0/aircrafts-data/<username>/", AircraftsView.as_view()),
]


# /api/v1.0/aircrafts-data/byhour
# /api/v1.0/aircrafts-data/Brazil
# /api/v1.0/airports-data/ALL
# /api/v1.0/airports-data/Brazil