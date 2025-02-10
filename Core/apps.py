from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Core'
    verbose_name ='Creditos e transaçoes'

    def ready(self):
        import Core.signals 