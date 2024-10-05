from django.contrib import admin
from .models import PromotionCode,Cart, CartItem, Wishlist

admin.site.register(PromotionCode)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
