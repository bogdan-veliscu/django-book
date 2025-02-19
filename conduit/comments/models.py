from django.db import models
import logging

from conduit.core.models import SoftDeletableModel
from conduit.profiles.models import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.debug("Loading Comment model module")

class Comment(SoftDeletableModel):
    class Meta:
        app_label = 'conduit_comments'
        
    logger.debug(f"Registering Comment model with app_label: {Meta.app_label}")

    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_comments')
    # Use string reference to avoid circular import
    article = models.ForeignKey('conduit_articles.Article', on_delete=models.CASCADE, related_name='article_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    logger.debug("Comment model class defined")

    def __str__(self):
        return f'Comment by {self.author.name} on {self.article.title}'

    @property
    def replies_count(self):
        return self.replies.count()

    def is_reply(self):
        return self.parent is not None
