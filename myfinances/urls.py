from django.urls import path, include
from myfinances.views import statement, home, categories

# To use API using rest framework
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register("categories", views.CategoriesView)
router.register("users", views.UsersView)


app_name = "myfinances"
urlpatterns = [
    path("", home, name="home"),
    path("statement/", statement, name="statement"),
    path("categories/", categories, name="categories"),
    path("api/", include(router.urls)),
]
