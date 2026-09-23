# urls.py

from django.urls import path
from . import views
from . import exports

urlpatterns = [
    # admin only
    path("admin-only/", views.admin_only_view, name="admin_only_view"),

    # Home
    path('', views.clinicdashpro_home, name='clinicdashpro_home'),

    # Upload pages
    path('upload/gusto/', views.upload_gusto, name='upload_gusto'),
    path('upload/xero/', views.upload_xero, name='upload_xero'),
    path('upload/jane_sessions/', views.upload_jane_sessions,
         name='upload_jane_sessions'),
    path("upload/jane/claims/", views.upload_jane_processed_claims,
         name="upload_jane_processed_claims"),

    # Success pages
    path('upload/gusto/success/', views.gusto_upload_success,
         name='gusto_upload_success'),
    path('upload/xero/success/', views.xero_upload_success,
         name='xero_upload_success'),
    path('upload/jane/sessions/success/', views.jane_sessions_upload_success,
         name='jane_sessions_upload_success'),
    path("upload/jane/claims/success/", views.jane_processed_claims_upload_success,
         name="jane_processed_claims_upload_success"),

    # Basic List view
    path("list/gusto/", views.gusto_list, name="gusto_list"),
    path("list/xero/", views.xero_list, name="xero_list"),
    path("list/jane/sessions/", views.jane_sessions_list,
         name="jane_sessions_list"),
    path("list/jane/claims/", views.jane_claims_list, name="jane_claims_list"),
    path("list/revenue_details_view/",
         views.revenue_details_view, name="revenue_details_view"),


    # Additional Reports
    path("reports/", views.reports_home,         name="reports_home"),

    # Export Routes
    path("export/csv/<str:model_name>/", exports.export_csv, name="export_csv"),
    path("export/excel/<str:model_name>/",
         exports.export_excel, name="export_excel"),
    path("export/df/csv/", exports.export_df_csv, name="export_df_csv"),
    path("export/df/excel/", exports.export_df_excel, name="export_df_excel"),


]
