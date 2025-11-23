from django.apps import AppConfig


class InfernoMotorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Inferno_Motors'

    def ready(self):
        import Inferno_Motors.signals
