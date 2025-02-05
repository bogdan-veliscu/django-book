# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = '/app/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media/'

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# Allowed hosts
ALLOWED_HOSTS = ['brandfocus.ai', 'localhost']