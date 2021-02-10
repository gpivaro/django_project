from django.urls import path, include
from . import views

urlpatterns = [
    # path for the index page
    path("", views.index, name="myhouseweather-index"),
    # path for API routes
    path("api-routes", views.api_routes, name="myhouseweather-api-routes"),
    # path for all json data
    path(
        "api/v1.0/weather-data/<int:last_hours>/",
        views.weather_data,
        name="weather_data",
    ),
    # path for Weather Openweathermap
    path(
        "api/v1.0/weather-api/<str:city>/",
        views.get_weather_api_data,
        name="get_weather_api_data",
    ),
    # path to show IP Address or the count of IPs
    path(
        "analytics/show-visitors/<str:granularity>/",
        views.show_visitors_ip,
        name="show_visitors_ip",
    ),
]

