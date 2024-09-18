
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.conf import settings

class ParentCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name           =       models.CharField(max_length=255, unique=True)
    parent_category =      models.ForeignKey(ParentCategory, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name =  models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name


class Products(models.Model):
    name =       models.CharField(max_length=255)
    description =models.TextField()
    price =      models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    SKU =        models.CharField(max_length=100, unique=True)
    inventory =  models.PositiveIntegerField()
    category =   models.ForeignKey(Category, related_name='product_categories', on_delete=models.SET_NULL, null=True)
    brand =      models.ForeignKey(Brand, related_name='product_brands', on_delete=models.SET_NULL, null=True, blank=True)
    image =      models.ImageField(upload_to='product_images/', blank=True, null=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Products, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)



    def __str__(self):
        return f"{self.product.name} Image"


class ProductVariant(models.Model):
    product = models.ForeignKey(Products, related_name='variants', on_delete=models.CASCADE)
    variant_name = models.CharField(max_length=255)
    variant_value = models.CharField(max_length=255)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name}:{self.variant_name} for {self.product.name}"

class Pricing(models.Model):
    product = models.ForeignKey(Products, related_name='pricing', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, default='GHS')

    def __str__(self):
        return f"Pricing for {self.product.name}"


class Tags(models.Model):
    product = models.ManyToManyField(Products, related_name='tags')
    tag = models.CharField(max_length=50)

    def __str__(self):
        return self.tag


class ProductReview(models.Model):
    product = models.ForeignKey(Products, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user}"

class SEO(models.Model):
    product = models.OneToOneField(Products, related_name='seo', on_delete=models.CASCADE)
    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()
    meta_keywords = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"SEO for {self.product.name}"

class ShippingInfo(models.Model):
    product = models.OneToOneField(Products, related_name='shipping_info', on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    dimensions = models.CharField(max_length=255)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    available_for_shipping = models.BooleanField(default=True)

    def __str__(self):
        return f"Shipping Info for {self.product.name}"
