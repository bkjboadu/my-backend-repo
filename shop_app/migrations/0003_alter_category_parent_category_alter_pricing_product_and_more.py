# Generated by Django 5.1 on 2024-09-06 18:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop_app", "0002_remove_pricing_end_date_remove_pricing_start_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="parent_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subcategories",
                to="shop_app.category",
            ),
        ),
        migrations.AlterField(
            model_name="pricing",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pricing",
                to="shop_app.products",
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="shop_app.products",
            ),
        ),
        migrations.AlterField(
            model_name="productreview",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reviews",
                to="shop_app.products",
            ),
        ),
        migrations.AlterField(
            model_name="products",
            name="brand",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="product_brands",
                to="shop_app.brand",
            ),
        ),
        migrations.AlterField(
            model_name="products",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="product_categories",
                to="shop_app.category",
            ),
        ),
        migrations.AlterField(
            model_name="productvariant",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variants",
                to="shop_app.products",
            ),
        ),
        migrations.AlterField(
            model_name="seo",
            name="product",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="seo",
                to="shop_app.products",
            ),
        ),
        migrations.AlterField(
            model_name="shippinginfo",
            name="product",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shipping_info",
                to="shop_app.products",
            ),
        ),
        migrations.AlterField(
            model_name="tags",
            name="product",
            field=models.ManyToManyField(related_name="tags", to="shop_app.products"),
        ),
    ]