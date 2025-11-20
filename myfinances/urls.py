from django.urls import path, include
from myfinances.views import statement, home, categories, manage_items, manage_statements

# To use the login view
from django.contrib.auth.views import LoginView

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
    path("manage_items/", manage_items,name="manage_items"),
    path("manage_statements/", manage_statements,name="manage_statements"),
    # path("login/", LoginView.as_view()),
]
