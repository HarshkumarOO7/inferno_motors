from django.apps import AppConfig


class InfernoMotorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Inferno_Motors'

    def ready(self):
        # Temporarily disable signals while debugging admin delete
        # import Inferno_Motors.signals
        pass
