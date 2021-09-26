from django.urls import path, include
from . import views
from .views import DataMeasView

urlpatterns = [
    # path for the index page
    path("", views.index, name="myhouseweather-index"),
    # path for the data page
    # path("data/", views.table_page, name="myhouseweather-table-data"),
    # Class-based view
    path("data/", DataMeasView.as_view(), name="myhouseweather-table-data"),
    # path for API routes
    path("api-routes", views.api_routes, name="myhouseweather-api-routes"),
    # path for all json data
    path(
        "api/v1.0/weather-data/<int:last_hours>/",
        views.weather_data,
        name="weather_data",
    ),
    path(
        "api/v1.0/weather-data-moving-average/<int:last_hours>/",
        views.weather_data_moving_average,
        name="weather_data_moving_average",
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

