from .models import Order, OrderItem
from inventory_management.models import Product
from celery import shared_task
from django.db import transaction
from typing import Dict
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
import requests,os
