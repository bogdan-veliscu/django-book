# Generated by Django 5.0.4 on 2024-05-20 16:20

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0003_user_first_name_user_last_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="created_at",
        ),
        migrations.RemoveField(
            model_name="user",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_active",
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_staff",
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_verified",
        ),
        migrations.RemoveField(
            model_name="user",
            name="last_name",
        ),
        migrations.RemoveField(
            model_name="user",
            name="updated_at",
        ),
        migrations.RemoveField(
            model_name="user",
            name="username",
        ),
        migrations.AddField(
            model_name="user",
            name="name",
            field=models.CharField(default=django.utils.timezone.now, max_length=60),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=254, unique=True, verbose_name="Email Address"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="image",
            field=models.URLField(blank=True, null=True),
        ),
    ]
