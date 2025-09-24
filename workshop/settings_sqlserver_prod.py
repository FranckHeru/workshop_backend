from .settings_base import *
import os

DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CORS_ALLOWED_ORIGINS = [o for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o]
CSRF_TRUSTED_ORIGINS = [o for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o]

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "!!-override-me-in-prod-!!")

# Sentry (opcional, solo si SENTRY_DSN está definido)
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENV = os.getenv("SENTRY_ENVIRONMENT", "prod")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENV,
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
        send_default_pii=False,
    )

# Base de datos SQL Server (mssql-django)
DATABASES = {
    "default": {
        "ENGINE": "mssql",
        "NAME": os.getenv("DB_NAME", "WorkshopDB"),
        "USER": os.getenv("DB_USER", "sa"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "192.168.3.20"),
        "PORT": os.getenv("DB_PORT", "50222"),
        "OPTIONS": {
            "driver": os.getenv("ODBC_DRIVER", "ODBC Driver 18 for SQL Server"),
            # extra_params permite TrustServerCertificate y Encrypt
            "extra_params": os.getenv("MSSQL_EXTRA", "TrustServerCertificate=yes;Encrypt=no;"),
        },
    }
}

STATIC_ROOT = os.getenv("STATIC_ROOT", os.path.join(BASE_DIR, "staticfiles"))
