from django.db import IntegrityError
from django.db.models import Count
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from taxi_app.models import *
from taxi_app.serializers import ClientSerializer, OrderSerializer, DriverSerializer

import requests, math


def client_index(request):
    return render(request, "taxi_app/client.html")


@api_view(["POST"])
@parser_classes((JSONParser,))
def client_registration(request):
    try:
        client = Client.objects.create(
            password=request.data["password"],
            surname=request.data["surname"],
            name=request.data["name"]
        )
        return Response({
            "status": True,
            "client_id": client.pk
        })
    except (KeyError, IntegrityError) as e:
        return Response({
            "status": False,
            "error": str(e)
        })


@api_view(["POST"])
@parser_classes((JSONParser,))
def client_authorization(request):
    try:
        client = get_object_or_404(
            Client,
            phone_number=request.data["phone_number"],
            password=request.data["password"],
        )
        return Response({
            "status": True,
            "client": ClientSerializer(client, many=False).data
        })
    except (KeyError, IntegrityError, Http404) as e:
        return Response({
            "status": False,
            "error": str(e)
        })


@api_view(["POST"])
@parser_classes((JSONParser,))
def client_create_new_order(request):
    try:
        order = Order.objects.create(
            client=get_object_or_404(Client, pk=request.data["client_id"]),
            address_from=request.data["address_from"],
            address_to=request.data["address_to"],
            is_child_seat_needed=request.data["is_child_seat_needed"],
            is_conditioner_needed=request.data["is_conditioner_needed"],
            payment_type=request.data["payment_type"],
            distance=request.data["distance"],
            price=request.data["price"],
        )
        return Response({
            "status": True,
            "order_id": order.pk,
            "order_detail": OrderSerializer(order, many=False).data
        })
    except (KeyError, IntegrityError) as e:
        return Response({
            "status": False,
            "error": str(e)
        })


@api_view(["POST"])
@parser_classes((JSONParser,))
def client_cancels_order(request):
    try:
        order = get_object_or_404(Order, pk=request.data["order_id"])
        order.order_status = "canceled"
        order.save()
        return Response({
            "status": True
        })
    except (KeyError, Http404) as e:
        return Response({
            "status": False,
            "error": str(e)
        })


@api_view(["POST"])
@parser_classes((JSONParser,))
def client_requests_favourite_destinations(request):
    try:
        fav_destinations = Order.objects.filter(
            client_id=request.data["client_id"]
        ).values("address_to").annotate(count=Count("address_to")).order_by('count')
        if fav_destinations.count() > 5:
            fav_destinations = fav_destinations[-5:]
        return Response({
            "status": True,
            "list": fav_destinations
        })
    except KeyError as e:
        return Response({
            "status": False,
            "error": str(e)
        })


@api_view(["POST"])
@parser_classes((JSONParser,))
def client_requests_driver_position(request):
    response = {"status": False}
    try:
        order = get_object_or_404(Order, pk=request.data["order_id"])
        if order.driver is not None:
            response["status"] = True
            response["driver_lat"] = order.driver.driver_lat
            response["driver_lng"] = order.driver.driver_lng
        else:
            response["error"] = "This order not accepted yet!!!"
    except (KeyError, Http404) as e:
        response["error"] = str(e)
    return Response(response)


@api_view(["POST"])
@parser_classes((JSONParser,))
def client_send_new_response_about_driver(request):
    try:
        order = get_object_or_404(Order, pk=request.data["order_id"])
        book = DriverResponsesBook.objects.get_or_create(driver=order.driver, client=order.client)
        book.responses.add(
            Response.objects.create(
                text=request.data["text"],
                response_type=request.data["response_type"]
            )
        )
        book.save()
        order.driver.new_like(request.data["response_type"])
        return Response({"status": True})
    except (KeyError, Http404) as e:
        return Response({
            "status": False,
            "error": str(e)
        })


@api_view(["POST"])
@parser_classes((JSONParser,))
def client_send_like_to_driver(request):
    try:
        order = get_object_or_404(Order, pk=request.data["order_id"])
        order.driver.new_like(request.data["like"])
        return Response({"status": True})
    except (KeyError, Http404) as e:
        return Response({
            "status": False,
            "error": str(e)
        })


@api_view(["POST"])
@parser_classes((JSONParser,))
def order_check_status(request):
    try:
        order = get_object_or_404(Order, pk=request.data["order_id"])
        return Response({
            "status": True,
            "order_status": order.order_status
        })
    except (KeyError, Http404) as e:
        return Response({
            "status": False,
            "error": str(e)
        })


@api_view(["POST"])
@parser_classes((JSONParser,))
def driver_registration(request):
    try:
        driver = Driver.objects.create(
            login=request.data["login"],
            password=request.data["password"],
            surname=request.data["surname"],
            name=request.data["name"],
            phone_number=request.data["phone_number"],
            vehicle_registration_plate=request.data["vehicle_registration_plate"],
            driver_lat=request.data["driver_lat"],
            driver_lng=request.data["driver_lng"],
        )
        return Response({
            "status": True,
            "driver_id": driver.pk
        })
    except (KeyError, IntegrityError) as e:
        return Response({
            "status": False,
            "error": str(e)
        })


@api_view(["POST"])
@parser_classes((JSONParser,))
def driver_authorization(request):
    try:
        driver = get_object_or_404(
            Driver,
            login=request.data["login"],
            password=request.data["password"]
        )
        return Response({
            "status": True,
            "driver_id": driver.pk,
            "driver_detail": DriverSerializer(driver, many=False).data
        })
    except (KeyError, Http404) as e:
        return Response({
            "status": False,
            "error": str(e)
        })


@api_view(["POST"])
@parser_classes((JSONParser,))
def driver_change_status(request):
    response = {"status": False}
    try:
        driver = get_object_or_404(
            Driver,
            pk=request.data["driver_id"]
        )
        if driver.driver_status is 3:
            response["error"] = "temp_blocked"
            response["from_date"] = driver.last_fail_date.date()
        elif driver.driver_status is 4:
            response["error"] = "blocked"
        else:
            driver.driver_status = request.data["driver_status"]
            response["status"] = True
    except (KeyError, Http404) as e:
        response["error"] = str(e)
    return Response(response)


# Need to test
@api_view(["POST"])
@parser_classes((JSONParser,))
def driver_requests_orders(request):
    try:
        import datetime
        driver = get_object_or_404(Driver, pk=request.data["driver_id"])
        driver.driver_lat = request.data["lat"]
        driver.driver_lng = request.data["lng"]
        driver.save()
        orders_request = []

        orders = Order.objects.filter(order_status="new", planed_date__range=(
            "2000-01-01",
            datetime.datetime.today().strftime("%Y-%m-%d")
        ))
        for order in orders:
            dist = distance((driver.driver_lat, driver.driver_lng), latlng(order.address_from))
            if dist <= driver.radius_of_order_accepting:
                orders_request.append({
                    "order": OrderSerializer(order, many=False).data,
                    "distance": dist
                })
        return Response({
            "status": True,
            "orders": orders_request
        })

    except (KeyError, Http404) as e:
        return Response({
            "status": False,
            "error": str(e)
        })


@api_view(["POST"])
@parser_classes((JSONParser,))
def driver_accept_order(request):
    response = {"status": False}
    try:
        driver = get_object_or_404(Driver, pk=request.data["driver_id"])
        order = get_object_or_404(Order, pk=request.data["order_id"])
        if order.order_status is "new":
            order.driver = driver
            order.order_status = "accepted"
            response["status"] = True
        else:
            response["error"] = "reserved"
    except (KeyError, Http404) as e:
        response["error"] = str(e)
    return Response(response)


@api_view(["POST"])
@parser_classes((JSONParser,))
def driver_arrived_to_client(request):
    response = {"status": False}
    try:
        order = get_object_or_404(Order, pk=request.data["order_id"])
        order.order_status = "arrived"
        response["status"] = True
    except (KeyError, Http404) as e:
        response["error"] = str(e)
    return Response(response)


@api_view(["POST"])
@parser_classes((JSONParser,))
def driver_start_ride(request):
    response = {"status": False}
    try:
        order = get_object_or_404(Order, pk=request.data["order_id"])
        order.order_status = "executing"
        response["status"] = True
    except (KeyError, Http404) as e:
        response["error"] = str(e)
    return Response(response)


@api_view(["POST"])
@parser_classes((JSONParser,))
def driver_finish_order(request):
    response = {"status": False}
    try:
        order = get_object_or_404(Order, pk=request.data["order_id"])
        order.order_status = "finished"
        response["status"] = True
    except (KeyError, Http404) as e:
        response["error"] = str(e)
    return Response(response)


@api_view(["POST"])
@parser_classes((JSONParser,))
def driver_cancel_order(request):
    response = {"status": False}
    try:
        driver = get_object_or_404(Driver, pk=request.data["driver_id"])
        order = get_object_or_404(Order, pk=request.data["order_id"])
        if order.driver is driver:
            order.driver = None
            order.order_status = "new"
            response["status"] = True
        else:
            response["error"] = "reserved"
    except (KeyError, Http404) as e:
        response["error"] = str(e)
    return Response(response)


@api_view(["POST"])
@parser_classes((JSONParser,))
def driver_confirm_cash_payment(request):
    try:
        pass
    except (KeyError, Http404) as e:
        return Response({
            "status": False,
            "error": str(e)
        })


def latlng(geocode):
    url = 'https://geocode-maps.yandex.ru/1.x/?format=json&geocode={0}'.format(geocode)
    lng, lat = requests.get(url)\
        .json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split(" ")
    return float(lat), float(lng)


def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    d_lat = math.radians(lat2-lat1)
    d_lon = math.radians(lon2-lon1)
    a = math.sin(d_lat/2) * math.sin(d_lat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(d_lon/2) * math.sin(d_lon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

