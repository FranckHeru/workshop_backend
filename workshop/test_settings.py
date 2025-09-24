# workshop/test_settings.py
import os
os.environ["DISABLE_USER_SEED"] = "1"  # evita crear usuarios seed en tests

from .settings import *  # noqa

# BD de tests en memoria, rapidísima y sin MSSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "file:memorydb_default?mode=memory&cache=shared",
        "TEST": {"NAME": "file:memorydb_default?mode=memory&cache=shared"},
        "OPTIONS": {"uri": True},
    }
}

# Acelera tests
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

DEBUG = True
TESTING = True

from .settings_flags import *
