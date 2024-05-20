from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if username is None:
            raise TypeError("Users must have a username.")

        if email is None:
            raise TypeError("Users must have an email address.")

        user = self.model(email=self.normalize_email(email), username=username)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, username, password=None):
        if password is None:
            raise TypeError("Superusers must have a password.")

        user = self.create_user(email, username, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=255, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return f"<User: {self.email}>"

    first_name: str = models.CharField(max_length=255, blank=True)
    last_name: str = models.CharField(max_length=255, blank=True)

    bio: str = models.TextField(blank=True)
    linkedin_url: str = models.URLField(blank=True)
    image: str | None = models.URLField(blank=True)

    followers = models.ManyToManyField(
        "self", related_name="followees", symmetrical=False
    )

    objects = UserManager()

    def get_full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username

    def get_short_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name}"
        else:
            return self.username

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
