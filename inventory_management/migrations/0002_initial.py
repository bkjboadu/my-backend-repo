# Generated by Django 5.1.1 on 2024-09-21 10:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("inventory_management", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="productreview",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="products",
            name="brand",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="product_brands",
                to="inventory_management.brand",
            ),
        ),
        migrations.AddField(
            model_name="products",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="product_categories",
                to="inventory_management.category",
            ),
        ),
        migrations.AddField(
            model_name="productreview",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reviews",
                to="inventory_management.products",
            ),
        ),
        migrations.AddField(
            model_name="productimage",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="inventory_management.products",
            ),
        ),
        migrations.AddField(
            model_name="pricing",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pricing",
                to="inventory_management.products",
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variants",
                to="inventory_management.products",
            ),
        ),
        migrations.AddField(
            model_name="seo",
            name="product",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="seo",
                to="inventory_management.products",
            ),
        ),
        migrations.AddField(
            model_name="shippinginfo",
            name="product",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shipping_info",
                to="inventory_management.products",
            ),
        ),
        migrations.AddField(
            model_name="tags",
            name="product",
            field=models.ManyToManyField(
                related_name="tags", to="inventory_management.products"
            ),
        ),
    ]