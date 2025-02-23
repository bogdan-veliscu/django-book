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

ALLOWED_HOSTS = [
    "localhost",
    "cod3.go.ro",
    "brandfocus.ai",
    "brandfocus.ai.s3.amazonaws.com",
    "134.122.66.29",
    "app",
    "host.docker.internal",
]

BLACKFIRE_ENABLED = True

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
    "drf_yasg",
    "rest_framework_simplejwt",
    "taggit",
    "channels",
    # local apps
    "conduit.profiles",
    "conduit.articles",
    "comments",
    "django.contrib.sites",
    "compressor",
    "storages",
    "corsheaders",
]

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1", "v2"],
    "VERSION_PARAM": "version",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

SITE_ID = 1

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
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Custom middleware
    "middleware.PerformanceLoggingMiddleware",
    "middleware.CustomSessionMiddleware",
    "middleware.CustomAuthenticationMiddleware",
    "middleware.GlobalCacheMiddleware",
    "middleware.CustomGZipMiddleware",
    "middleware.QueryCountMiddleware",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",  # Django development URL
    "http://localhost:3000",  # Next.js app's development URL
    "https://brandfocus.ai",  # Next.js app's production URL
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
ASGI_APPLICATION = "config.asgi.application"

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


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "profiles.User"

EMAIL_HOST = os.getenv("SMTP_HOST", default="smtp.gmail.com")
EMAIL_HOST_USER = os.getenv("SMTP_USER")
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_PORT = os.getenv("SMTP_PORT", default=587)
EMAIL_USE_TLS = os.getenv("SMTP_TLS", default=True)

# AWS S3 settings
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

# Static files (CSS, JavaScript, images)
STATIC_URL = "/static/"
MEDIA_URL = "/media/"


MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "static")
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

COMPRESS_ENABLED = True
COMPRESS_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
COMPRESS_URL = STATIC_URL
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_OUTPUT_DIR = "CACHE"

COMPRESS_ENABLED = False  # Typically set to False in development and True in production
COMPRESS_OFFLINE = False  # Enables offline compression, useful for production


# Assuming Cloudflare is handling SSL
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Enforce HTTPS
# SECURE_SSL_REDIRECT = True

# Ensure cookies are only sent over HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Security middleware
SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


GLOBAL_CACHE_TIME = 300  # 5 minutes
