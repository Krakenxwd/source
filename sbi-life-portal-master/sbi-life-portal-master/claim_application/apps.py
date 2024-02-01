from django.apps import AppConfig


class ClaimApplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'claim_application'

    def ready(self):
        import claim_application.signals