from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name ='Afiliados e Saques'

    def ready(self):
        import accounts.signals 