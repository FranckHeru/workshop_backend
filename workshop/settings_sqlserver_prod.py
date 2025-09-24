import os
from .settings_sqlserver import *  # o desde settings_base según tu estructura

# Forzamos a tomar password del entorno (DB_PASSWORD o WORKSHOP_SQL_SA_PWD)
DATABASES["default"]["USER"] = os.environ.get("DB_USER", DATABASES["default"].get("USER", "sa"))
DATABASES["default"]["PASSWORD"] = (
    os.environ.get("DB_PASSWORD")
    or os.environ.get("WORKSHOP_SQL_SA_PWD")
    or ""
)


# --- Hardened production toggles (appended) ---
import os as _os
DEBUG = False
SECRET_KEY = _os.environ.get('SECRET_KEY','change-me')
ALLOWED_HOSTS = [h for h in _os.environ.get('ALLOWED_HOSTS','localhost,127.0.0.1').split(',') if h]
CORS_ALLOWED_ORIGINS = [u for u in _os.environ.get('CORS_ALLOWED_ORIGINS','').split(',') if u]
CSRF_TRUSTED_ORIGINS = [u for u in _os.environ.get('CSRF_TRUSTED_ORIGINS','').split(',') if u]
SENTRY_DSN = _os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(_os.environ.get("SENTRY_TRACES","0.1")),
        environment=_os.environ.get('ENVIRONMENT','prod'),
    )
