from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "conduit.articles"
    label = "conduit_articles"

    def ready(self) -> None:
        import conduit.articles.signals  # noqa
