"""Common Django settings for all environments.
Ruta esperada del proyecto: C:\\Taller\\workshop_backend\\backend
"""
from pathlib import Path
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar .env simple (sin dependencias):
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if not line or line.strip().startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "!!-REEMPLAZA-ESTO-EN-PROD-!!")
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()] or ["localhost", "127.0.0.1"]

# Apps básicas + DRF + Spectacular
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "drf_spectacular",
    "django_filters",
    "corsheaders",

    # Apps del proyecto
    "core",
    "customers",
    "vehicles",
    "catalog",
    "quotes",
    "workorders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "workshop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "workshop.wsgi.application"

# Base de datos (por defecto sqlite para dev). Para SQL Server, usa settings_prod.
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("DB_USER", ""),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", ""),
        "PORT": os.environ.get("DB_PORT", ""),
        "OPTIONS": {},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es"
TIME_ZONE = "America/El_Salvador"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === DRF + JWT + Spectacular centralizados ===
from .drf_config import *  # noqa: F401,F403

# === Logging estructurado (config por dict) ===
from .logging_config import LOGGING  # noqa: F401

# === CORS/CSRF (listas explícitas) ===
CORS_ALLOWED_ORIGINS = [o for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]
CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "1") == "1"
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "1") == "1"
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "1") == "1"
SECURE_REFERRER_POLICY = os.environ.get("SECURE_REFERRER_POLICY", "strict-origin-when-cross-origin")
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get("SECURE_HSTS_INCLUDE_SUBDOMAINS", "1") == "1"
SECURE_HSTS_PRELOAD = os.environ.get("SECURE_HSTS_PRELOAD", "1") == "1"
SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = os.environ.get("CSRF_COOKIE_SAMESITE", "Lax")

# === Sentry (opcional) ===
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
SENTRY_TRACES = float(os.environ.get("SENTRY_TRACES", "0"))
RELEASE = os.environ.get("RELEASE")

# Detectar release desde VERSION.txt si no viene por env
try:
    if not RELEASE:
        vfile = BASE_DIR / "VERSION.txt"
        if vfile.exists():
            RELEASE = vfile.read_text(encoding="utf-8").strip()
except Exception:
    RELEASE = None  # no bloquear carga de settings si falla

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=SENTRY_TRACES,  # 0.0 desactiva APM
        send_default_pii=False,
        environment="prod" if not DEBUG else "dev",
        release=RELEASE,
    )
