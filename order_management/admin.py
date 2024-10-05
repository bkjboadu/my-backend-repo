from django.contrib import admin
from .models import OrderItem, Order, Payment, Shipment

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Shipment)
