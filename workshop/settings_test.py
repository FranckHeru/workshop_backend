from .settings_prod import *  # noqa

SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

try:
    REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
except Exception:
    pass

ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
