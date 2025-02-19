# Generated by Django 5.0.4 on 2024-05-15 21:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conduit_articles", "0002_article_author_published_articles"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="favorites",
            field=models.ManyToManyField(
                blank=True,
                related_name="favorites",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
