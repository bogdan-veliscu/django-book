import io
import logging

import markdown
from core.models import SoftDeletableModel
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
)
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
from taggit.managers import TaggableManager

from conduit.profiles.models import User
from conduit.comments.models import Comment

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.debug("Loading Article model module")

User = get_user_model()


class ArticleQuerySet(models.QuerySet):
    def with_favorites(self, user: AnonymousUser | User) -> models.QuerySet:
        return self.annotate(
            num_favorites=models.Count("favorites"),
            is_favorite=(
                models.Exists(
                    get_user_model().objects.filter(
                        pk=user.id, favorites=models.OuterRef("pk")
                    )
                )
                if user.is_authenticated
                else models.Value(False, output_field=models.BooleanField())
            ),
        )

    def published(self):
        return self.filter(status="published")

    def with_author(self):
        return self.select_related("author")

    def with_comments_count(self):
        return self.annotate(comments_count=Count("comments"))


class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


class Article(SoftDeletableModel):
    class Meta:
        app_label = 'conduit_articles'
        
    logger.debug(f"Registering Article model with app_label: {Meta.app_label}")
    logger.debug(f"Module path: {__name__}")

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    summary = models.TextField(blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10,
        choices=[("draft", "Draft"), ("published", "Published")],
        default="draft",
    )
    comments = models.ManyToManyField(
        User,
        through='conduit_comments.Comment',
        related_name='commented_articles'
    )
    tags = TaggableManager(blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_articles', blank=True)

    logger.debug("Article model class defined")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.image:
            pil_image = Image.open(self.image)
            if pil_image.mode in ("RGBA", "P"):
                pil_image = pil_image.convert("RGB")

            pil_image = pil_image.resize((800, 800), Image.Resampling.LANCZOS)

            new_image = io.BytesIO()
            pil_image.save(new_image, format="JPEG", quality=75)

            temp_name = self.image.name
            self.image = InMemoryUploadedFile(
                new_image,
                "ImageField",
                "%s.jpg" % temp_name.split(".")[0],
                "image/jpeg",
                new_image.tell,
                None,
            )

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "article_detail", kwargs={"article_id": self.id, "slug": self.slug}
        )

    def as_markdown(self):
        return markdown.markdown(self.content, safe_mode="escape")

    @property
    def favorites_count(self):
        return self.favorites.count()

    @property
    def comments_count(self):
        return self.comments.count()

    def is_favorited_by(self, user):
        return self.favorites.filter(id=user.id).exists()

    def add_favorite(self, user):
        if not self.is_favorited_by(user):
            self.favorites.add(user)

    def remove_favorite(self, user):
        if self.is_favorited_by(user):
            self.favorites.remove(user)

    def is_published(self):
        return self.status == "published"


def create_model(
    name, fields=None, app_label="", module="", options=None, admin_opts=None
):
    class Meta:
        pass

    if app_label:
        Meta.app_label = app_label

    if options is not None:
        for key, value in options.items():
            setattr(Meta, key, value)

    attrs = {"__module__": module, "Meta": Meta}

    if fields:
        attrs.update(fields)

    model = type(name, (models.Model,), attrs)

    if admin_opts is not None:

        class Admin:
            pass

        for key, value in admin_opts.items():
            setattr(Admin, key, value)

        model.Admin = Admin

    return model


# # Define the fields for the model
# fields = {
#     "name": models.CharField(max_length=255),
#     "age": models.IntegerField(),
# }

# # Define the meta options for the model
# options = {
#     "ordering": ["name"],
#     "verbose_name": "DynamicModel",
# }

# # Create the model
# DynamicModel = create_model("DynamicModel", fields, app_label="myapp", options=options)

# # Now you can use DynamicModel like any other Django model
# instance = DynamicModel(name="Test", age=30)
# instance.save()
