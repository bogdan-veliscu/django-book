from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from conduit.comments.models import Comment


@receiver(post_save, sender=Comment)
def update_article_comments_count_on_save(sender, instance, created, **kwargs):
    """Update article's comments count when a comment is created or updated."""
    if created:
        article = instance.article
        article.comments_count = article.comments.count()
        article.save(update_fields=['comments_count'])


@receiver(post_delete, sender=Comment)
def update_article_comments_count_on_delete(sender, instance, **kwargs):
    """Update article's comments count when a comment is deleted."""
    article = instance.article
    article.comments_count = article.comments.count()
    article.save(update_fields=['comments_count']) 