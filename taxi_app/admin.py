from django.contrib import admin

from taxi_app.models import Order, Driver, DriverResponsesBook, Client, Settings

admin.site.register(Order)
admin.site.register(Driver)
admin.site.register(DriverResponsesBook)
admin.site.register(Client)
admin.site.register(Settings)
