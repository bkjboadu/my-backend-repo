from django.apps import AppConfig


class OrderTrackingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "order_tracking"

    def ready(self):
        import order_tracking.signals
