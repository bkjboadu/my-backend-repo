from django.contrib import admin
from .models import (
    Category,
    Brand,
    Products,
    ProductReview,
    Pricing,
    ProductImage,
    ProductVariant,
    Tags,
    SEO,
    ShippingInfo,
)

admin.site.register(Category),
admin.site.register(Brand),
admin.site.register(Products),
admin.site.register(ProductReview),
admin.site.register(ProductImage),
admin.site.register(ProductVariant),
admin.site.register(Tags),
admin.site.register(Pricing),
admin.site.register(SEO),
admin.site.register(ShippingInfo)
