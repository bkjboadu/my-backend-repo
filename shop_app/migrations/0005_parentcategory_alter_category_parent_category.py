# Generated by Django 5.1 on 2024-09-10 11:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop_app", "0004_remove_category_description_remove_category_slug_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ParentCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name="category",
            name="parent_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="shop_app.parentcategory",
            ),
        ),
    ]