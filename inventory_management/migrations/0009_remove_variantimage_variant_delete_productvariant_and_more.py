# Generated by Django 5.1.1 on 2024-10-28 19:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory_management", "0008_alter_productimage_product_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="variantimage",
            name="variant",
        ),
        migrations.DeleteModel(
            name="ProductVariant",
        ),
        migrations.DeleteModel(
            name="VariantImage",
        ),
    ]