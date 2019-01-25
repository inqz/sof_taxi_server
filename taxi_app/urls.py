from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from taxi_app import views

app_name = "taxi_app"

urlpatterns = [
    path("client/registration/", views.client_registration),
    path("client/authorization/", views.client_authorization),
    path("client/order/create/", views.client_create_new_order),
    path("client/order/cancel/", views.client_cancels_order),
    path("client/order/detail/", views.get_order_detail),
    path("client/request/destinations/", views.client_requests_favourite_destinations),
    path("client/request/driver/position/", views.client_requests_driver_position),
    path("client/driver/like/", views.client_send_like_to_driver),
    path("client/driver/response/", views.client_send_new_response_about_driver),
    path("driver/registration/", views.driver_registration),
    path("driver/authorization/", views.driver_authorization),
    path("driver/status/change/", views.driver_change_status),
    path("driver/request/orders/", views.driver_requests_orders),
    path("driver/order/accept/", views.driver_accept_order),
    path("driver/order/arrived/", views.driver_arrived_to_client),
    path("driver/order/ride/", views.driver_start_ride),
    path("driver/order/finish/", views.driver_finish_order),
    path("driver/order/cancel/", views.driver_cancel_order),
    path("driver/order/detail/", views.get_order_detail),
]

urlpatterns += [
    path('doc/', get_swagger_view(title='API doc'))
]
