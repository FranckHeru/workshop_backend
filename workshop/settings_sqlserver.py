# workshop/settings_sqlserver.py
from .settings import *   # hereda TODO
import os
from pathlib import Path

BASE_DIR = Path(BASE_DIR)
STATICFILES_DIRS = [p for p in (BASE_DIR / "static",) if p.exists()]

_base = {}
try:
    _base = JAZZMIN_SETTINGS
except NameError:
    pass

JAZZMIN_SETTINGS = {
    **_base,
    "site_brand": "Workshop",
    "site_logo": "img/login_logo.png",
    "login_logo": "img/login_logo.png",
    "login_background": "img/login_bg.png",
    "custom_css": "css/admin_overrides.css",
    # <<< solo 1 JS aquí (evitamos el bug del valor string con corchetes)
    "custom_js": "js/admin_overrides.js",
    "related_modal_active": True,
}

X_FRAME_OPTIONS = "SAMEORIGIN"

DATABASES = {
    "default": {
        "ENGINE": "mssql",
        "NAME": os.environ.get("SQLSERVER_DB", "WorkshopDB"),
        "USER": os.environ.get("SQLSERVER_USER", "sa"),
        "PASSWORD": os.environ.get("SQLSERVER_PASSWORD", ""),
        "HOST": os.environ.get("SQLSERVER_HOST", "localhost"),
        "PORT": os.environ.get("SQLSERVER_PORT", ""),
        "OPTIONS": {
            "driver": os.environ.get("SQLSERVER_DRIVER", "ODBC Driver 18 for SQL Server"),
            "extra_params": os.environ.get(
                "SQLSERVER_EXTRA",
                "Encrypt=yes;TrustServerCertificate=yes;",
            ),
        },
    }
}
