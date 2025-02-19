from django.apps import AppConfig
from django.conf import settings


class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "conduit.profiles"
    label = "conduit_profiles"

    def ready(self):
        print(f"Loaded profiles app with label: {self.label}")
        print(f"User model path: {settings.AUTH_USER_MODEL}")
        import conduit.profiles.signals  # noqa
