"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # urls for admin site
    path("admin/", admin.site.urls),
    # urls for register on the blog app
    path("register/", user_views.register, name="register"),
    # urls for profile on the blog app
    path("profile/", user_views.profile, name="profile"),
    # urls for login on the blog app
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    # urls for logout on the blog app
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
    # urls for password-reset on the blog app
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"),
        name="password_reset",
    ),
    # urls for password-reset done on the blog app
    path(
        "password-reset/done",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    # urls for password-reset confirm on the blog app
    path(
        "password-reset-confirm/<uidb64>/<token>",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    # urls for password-reset complete on the blog app
    path(
        "password-reset-complete",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # urls for the blog app
    path("blog/", include("blog.urls")),
    # urls for the main page of the project (resume app)
    path("", include("resumesite.urls")),
    # urls for the airtraffic app
    path("airtraffic/", include("airtrafficapp.urls")),
    # urls for the myhouseweather app
    path("homeweather/", include("myhouseweatherapp.urls")),
    # urls for the Analyticsapp
    path("analytics/", include("analyticsapp.urls")),
    # urls for the Myfinances
    path("myfinances/", include("myfinances.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

