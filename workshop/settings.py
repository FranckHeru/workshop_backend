# workshop/settings.py (v4) – con integración de quotes y Swagger/Redoc
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    # Terceros y base
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",  # ← añadido para servir assets del Swagger/Redoc UI
    "django_filters",
    "corsheaders",
    "rest_framework.authtoken",

    # Apps del proyecto
    "core",
    "customers.apps.CustomersConfig",
    "vehicles.apps.VehiclesConfig",
    "workorders.apps.WorkordersConfig",
    "catalog.apps.CatalogConfig",
    "quotes.apps.QuotesConfig",  # ← NUEVO
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
        "DIRS": [],
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuración REST Framework + JWT
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Configuración Swagger/Redoc
SPECTACULAR_SETTINGS = {
    "TITLE": "Workshop API",
    "DESCRIPTION": "API de taller mecánico (clientes, vehículos, órdenes de trabajo, catálogo, cotizaciones).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Jazzmin UI
JAZZMIN_SETTINGS = {
    "site_title": "Workshop Admin",
    "site_header": "Workshop",
    "site_brand": "Workshop",
    "welcome_sign": "Bienvenido al panel del Taller",
    "site_logo": "img/logo.png",
    "login_logo": "img/logo.png",
    "custom_css": "css/jazzmin_overrides.css",

    # Abrir relaciones en modal
    "related_modal_active": True,
    "related_modal_warn_on_unsaved": True,

    # Menú superior en español
    "topmenu_links": [
        {"name": "Inicio", "url": "admin:index"},
        {"name": "Clientes", "url": "admin:customers_customer_changelist"},
        {"name": "Vehículos", "url": "admin:vehicles_vehicle_changelist"},
        {"name": "Órdenes de trabajo", "url": "admin:workorders_workorder_changelist"},
        {"name": "Catálogo", "url": "admin:catalog_service_changelist"},
        {"name": "Cotizaciones", "url": "admin:quotes_quotation_changelist"},  # ← NUEVO
        {"name": "Swagger", "url": "/api/schema/swagger-ui/"},
        {"name": "ReDoc", "url": "/api/schema/redoc/"},
    ],

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "catalog": "fas fa-toolbox",
        "customers": "fas fa-user-friends",
        "vehicles": "fas fa-car-side",
        "workorders": "fas fa-clipboard-list",
        "quotes": "fas fa-file-invoice-dollar",  # ← NUEVO
    },

    "order_with_respect_to": ["customers", "vehicles", "workorders", "catalog", "quotes"],
    "show_ui_builder": False,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "cyborg",
    "dark_mode_theme": "darkly",
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
    "brand_colour": "navbar-dark",
    "accent": "accent-info",
}
