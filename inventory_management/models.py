from django.core.files import storage
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from storages.backends.gcloud import GoogleCloudStorage


# Store Model: Represents each store or tenant
class Store(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name




# Product Model
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)

    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("store", "sku")

    def __str__(self):
        return self.name


# Product Image Model
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_images"
    )
    image = models.ImageField(
        upload_to="media/product_images/", storage=GoogleCloudStorage()
    )
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_main = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(
                is_main=False
            )

        if not ProductImage.objects.filter(product=self.product).exists():
            self.is_main = True
        super(ProductImage, self).save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name}"


# Product Review Model
class ProductReview(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    name = models.CharField(max_length=255,null=False,blank=False)
    email = models.EmailField(null=True,blank=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "name")

    def __str__(self):
        return f"Review for {self.product.name} by {self.name}"


# Stock Entry Model
class StockEntry(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="stock_entries"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stock_entries"
    )
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_updates",
    )

    def __str__(self):
        return f"{self.quantity} units for {self.product.name}"
