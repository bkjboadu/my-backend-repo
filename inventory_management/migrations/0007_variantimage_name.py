# Generated by Django 5.1.1 on 2024-10-17 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory_management", "0006_variantimage_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="variantimage",
            name="name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]