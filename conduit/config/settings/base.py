"""
Django settings for conduit project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import read_dotenv

# from os.path import dirname, join


# project_dir = dirname(dirname(__file__))
# read .env file for parent directory
# read_dotenv(join(project_dir, ".env"))


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SITE_ID = 1

ALLOWED_HOSTS = ["localhost", "cod3.go.ro", "brandfocus.ai"]

APPEND_SLASH = False

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "taggit",
    # local apps
    "profiles",
    "articles",
    "comments",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "two_factor",
    # social auth
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.apple",
]

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ]
}

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# JWT token settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Token",),
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    # "shard1": {
    #     "ENGINE": "django.db.backends.postgresql",
    #     "NAME": os.getenv("POSTGRES_DB", default="conduit"),
    #     "USER": os.getenv("POSTGRES_USER", default="conduit"),
    #     "PASSWORD": os.getenv("POSTGRES_PASSWORD", default="conduit"),
    #     "HOST": os.getenv("POSTGRES_SHARD1_SERVER", default="localhost"),
    #     "PORT": os.getenv("POSTGRES_SHARD1_PORT", default="5432"),
    # },
    # "shard2": {
    #     "ENGINE": "django.db.backends.postgresql",
    #     "NAME": os.getenv("POSTGRES_DB", default="conduit"),
    #     "USER": os.getenv("POSTGRES_USER", default="conduit"),
    #     "PASSWORD": os.getenv("POSTGRES_PASSWORD", default="conduit"),
    #     "HOST": os.getenv("POSTGRES_SHARD2_SERVER", default="localhost"),
    #     "PORT": os.getenv("POSTGRES_SHARD2_PORT", default="5432"),
    # },
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", default="conduit"),
        "USER": os.getenv("POSTGRES_USER", default="conduit"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", default="conduit"),
        "HOST": os.getenv("POSTGRES_DEFAULT_SERVER", default="localhost"),
        "PORT": os.getenv("POSTGRES_DEFAULT_PORT", default="5432"),
    },
}

# DATABASE_ROUTERS = ["config.database_routers.ShardRouter"]


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "profiles.User"

EMAIL_HOST = os.getenv("SMTP_HOST", default="smtp.gmail.com")
EMAIL_HOST_USER = os.getenv("SMTP_USER")
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_PORT = os.getenv("SMTP_PORT", default=587)
EMAIL_USE_TLS = os.getenv("SMTP_TLS", default=True)


LOGIN_URL = "two_factor:login"

# this one is optional
LOGIN_REDIRECT_URL = "two_factor:profile"
