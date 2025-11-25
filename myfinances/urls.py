from django.urls import path, include
from myfinances.views import home, categories, statement, manage_items, manage_statements, banktransactions
from myfinances.views import (CategoryListListView,
                              CategoryListDetailView,
                              CategoryListCreateView,
                              CategoryListUpdateView,
                              CategoryListDeleteView,
                              TransactionsListView,
                              TransactionsDetailView,
                              TransactionsUpdateView,
                              TransactionsDeleteView)

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
    path("manage_items/", manage_items, name="manage_items"),
    path("manage_statements/", manage_statements, name="manage_statements"),
    path("categories-list/", CategoryListListView.as_view(), name="categories-list"),
    path("category/<int:pk>/", CategoryListDetailView.as_view(),
         name="category-detail"),
    path("category/new/", CategoryListCreateView.as_view(), name="category-new"),
    path("category/<int:pk>/update/",
         CategoryListUpdateView.as_view(), name="category-update"),
    path("category/<int:pk>/delete/",
         CategoryListDeleteView.as_view(), name="category-delete"),
    # path("login/", LoginView.as_view()),
    path("banktransactions/", banktransactions, name="banktransactions"),
    path("transactions-list/", TransactionsListView.as_view(),
         name="transactions-list"),
    path("transaction/<int:pk>/", TransactionsDetailView.as_view(),
         name="transactions-detail"),
    path("transaction/<int:pk>/update/",
         TransactionsUpdateView.as_view(), name="transactions-update"),
    path("transaction/<int:pk>/delete/",
         TransactionsDeleteView.as_view(), name="transactions-delete"),
]
