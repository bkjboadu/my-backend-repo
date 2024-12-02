from django.contrib import admin
from .models import (
    Product,
    ProductImage,
    ProductReview,
    StockEntry,
    Store,
)

admin.site.register(ProductReview)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Store)
admin.site.register(StockEntry)
