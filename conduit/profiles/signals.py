from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def initialize_user_profile(sender, instance, created, **kwargs):
    """Initialize user profile fields when a user is created."""
    if created:
        # Set default values for profile fields if needed
        if not instance.bio:
            instance.bio = ""
        if not instance.linkedin_url:
            instance.linkedin_url = ""
        instance.save() 