from django.contrib import admin
from django.urls import path
from storage.views import home, flights_page, flight_versions_page
from ledger.views import chain_info_view

urlpatterns = [
    path("", home, name="home"),
    path("flights/", flights_page, name="flights_page"),
    path("flights/<str:flight_id>/", flight_versions_page, name="flight_versions_page"),
    path("api/chain-info/", chain_info_view, name="chain-info"),
    path("admin/", admin.site.urls),
]
