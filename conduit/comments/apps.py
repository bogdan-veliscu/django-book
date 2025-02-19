from django.apps import AppConfig


class CommentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "conduit.comments"
    label = "conduit_comments"

    def ready(self):
        import conduit.comments.signals
