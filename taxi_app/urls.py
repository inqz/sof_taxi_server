from django.urls import path
from . import views

app_name = "taxi_app"

urlpatterns = [
    path("route/", views.latlng),
    path("client/", views.client_index),
    path("client/registration/", views.client_registration),
    path("client/authorization/", views.client_authorization),
    path("client/order/create/", views.client_create_new_order),
    path("client/order/cancel/", views.client_cancels_order),
    path("client/request/destinations/", views.client_requests_favourite_destinations),
    path("client/request/driver/position/", views.client_requests_driver_position),
    path("driver/request/orders/", views.driver_requests_orders)
]