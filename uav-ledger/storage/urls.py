from django.urls import path
from .views import ListFlightsView, ListVersionsView

urlpatterns = [
    path("flights", ListFlightsView.as_view(), name="list_flights"),
    path("versions/<str:flight_id>", ListVersionsView.as_view(), name="list_versions"),
]
