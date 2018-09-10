from rest_framework import serializers
from .models import *


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = 'id', 'name', 'surname', 'phone_number'


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = (
            'id'
            'surname',
            'name',
            'phone_number',
            'vehicle_registration_plate',
            'money_balance',
            'driver_lat',
            'driver_lng',
        )


class OrderSerializer(serializers.ModelSerializer):
    client = ClientSerializer(many=False, read_only=True)
    driver = DriverSerializer(many=False, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "client",
            "driver",
            "address_from",
            "address_to",
            "distance",
            "is_child_seat_needed",
            "is_conditioner_needed",
            "order_status",
            "payment_type",
            "price",
            "planed_date",
            "planed_time",
        )

