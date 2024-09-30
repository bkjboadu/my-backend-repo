from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductImage,
    ProductVariant,
    Supplier,
    StockEntry,
    Store
)

admin.site.register(Category),
admin.site.register(Product),
admin.site.register(ProductImage),
admin.site.register(ProductVariant),
admin.site.register(Supplier)
admin.site.register(Store)
admin.site.register(StockEntry)
