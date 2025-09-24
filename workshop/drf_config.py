from datetime import timedelta

REST_FRAMEWORK = {
    # Versionado por URL (prefix /api/v1/). Mantén compat con /api/ si hace falta.
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ("v1",),

    # Paginación por defecto (PageNumber)
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,

    # Throttling básico (ajusta límites a tu gusto)
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
        "user": "120/min",
    },

    # Auth (JWT si ya lo usas)
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],

    # OpenAPI / drf-spectacular
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Workshop API",
    "DESCRIPTION": "API estable v1 para Taller Automotriz",
    "VERSION": "1.0.0",  # versión del contrato OpenAPI
    "SERVERS": [
        {"url": "https://api.taller.example.com", "description": "Prod"},
        {"url": "https://staging.taller.example.com", "description": "Staging"},
        {"url": "http://localhost:8000", "description": "Local"},
    ],
}
