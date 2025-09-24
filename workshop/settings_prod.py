"""Production-hardened settings.
Usar: set DJANGO_SETTINGS_MODULE=workshop.settings_prod
"""
import os  # aseguramos disponibilidad local
from .settings_base import *  # noqa

DEBUG = False
# ALLOWED_HOSTS deben venir de env y ser explícitos.
assert ALLOWED_HOSTS and ALLOWED_HOSTS != ["localhost", "127.0.0.1"], "ALLOWED_HOSTS debe configurarse explícitamente en producción"

# SQL Server (ejemplo con django-mssql-backend / mssql-django)
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "mssql"),
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        # Para instancias nombradas puedes usar: 192.168.3.20\\APPSGS
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "1433"),
        "OPTIONS": {
            "driver": os.environ.get("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
            # Recomendado con ODBC18 si usas certificados self-signed:
            # Encrypt=yes;TrustServerCertificate=yes
            "extra_params": os.environ.get("DB_EXTRA_PARAMS", "Encrypt=no;TrustServerCertificate=yes"),
            # "host_is_server": True,  # <-- importante para host+puerto (quítalo cuando uses dB_HOST=tcp:...)
        },
        # Base de datos para pruebas (manage.py test)
        "TEST": {
            "NAME": os.environ.get("DB_TEST_NAME", "test_WorkshopDB"),
        },
    }
}

# Seguridad adicional
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if os.environ.get("BEHIND_PROXY", "1") == "1" else None
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
