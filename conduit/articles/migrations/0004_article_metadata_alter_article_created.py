# Generated by Django 5.0.4 on 2024-05-18 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conduit_articles", "0003_alter_article_favorites"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="metadata",
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name="article",
            name="created",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
