from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderTracking


def update_order_status(sender, instance, **kwargs):
    order = instance.order
    if instance.status == 'delivered':
        order.status = 'delivered'
    elif instance.status == 'failed':
        order.status = 'failed_delivery'
    order.save()


def update_order_status(sender, instance, **kwargs):
    order = instance.order
    if instance.status == "delivered":
        order.status = "delivered"
    elif instance.status == "failed":
        order.status = "failed_delivery"
    order.save()

