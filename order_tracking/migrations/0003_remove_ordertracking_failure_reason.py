# Generated by Django 5.1.1 on 2024-10-13 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("order_tracking", "0002_ordertracking_failure_reason"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ordertracking",
            name="failure_reason",
        ),
    ]