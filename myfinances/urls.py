from django.urls import path, include
from myfinances.views import statement_upload, home

app_name = "myfinances"
urlpatterns = [
    path("", home, name="home"),
    path("statement/", statement_upload, name="statement_upload"),
]
