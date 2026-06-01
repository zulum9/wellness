from django.apps import AppConfig


class MainAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main_app"  # Replace with your actual app directory name

    def ready(self):
        # Implicitly connects the signal handlers on app initialization
        import main_app.signals
