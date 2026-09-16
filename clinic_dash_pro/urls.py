# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.clinicdashpro_home, name='clinicdashpro_home'),

    # Upload pages
    path('upload/gusto/', views.upload_gusto, name='upload_gusto'),
    # path('upload/xero/', views.upload_xero, name='upload_xero'),
    # path('upload/jane/', views.upload_jane, name='upload_jane'),

    # Success pages
    path('upload/gusto/success/', views.gusto_upload_success,
         name='gusto_upload_success'),
    # path('upload/xero/success/', views.xero_upload_success,
    #      name='xero_upload_success'),
    # path('upload/jane/success/', views.jane_upload_success,
    #      name='jane_upload_success'),
]
