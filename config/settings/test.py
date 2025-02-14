"""
Test settings for the Django application.
"""
from .base import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "test-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "test_db"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "test_db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 0,  # Close connections after each test
    }
}

# Use in-memory cache for testing
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Use console email backend for testing
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable password hashers for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use fast template loaders
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # type: ignore
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# Disable migrations for tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Configure test runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Test-specific apps
INSTALLED_APPS += [  # type: ignore
    "pytest_factoryboy",
]

# Test-specific middleware
# You can add test-specific middleware here if needed

# Configure logging for tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

# Test media settings
MEDIA_ROOT = os.path.join(BASE_DIR, "test_media")  # type: ignore
MEDIA_URL = "/test-media/"

# Test static settings
STATIC_ROOT = os.path.join(BASE_DIR, "test_static")  # type: ignore
STATIC_URL = "/test-static/" 