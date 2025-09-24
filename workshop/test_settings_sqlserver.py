# workshop/test_settings_sqlserver.py
from .settings import *  # importa tu settings base del proyecto

# Evita que el seed cree usuarios demo durante los tests (así no choca con los usuarios del test)
DISABLE_USER_SEED = True

# DRF / DEBUG (opcional)
DEBUG = False

# Base de datos: SQL Server en 192.168.3.20\APPSGS usando ODBC Driver 18
DATABASES = {
    "default": {
        "ENGINE": "mssql",  # con el paquete mssql-django
        "NAME": "test_WorkshopDB",
        "USER": "sa",
        "PASSWORD": "WolfIT2025$%&",
        "HOST": r"192.168.3.20\APPSGS",  # OJO: doble backslash si editas en string normal
        "PORT": "",
        "OPTIONS": {
            "driver": "ODBC Driver 18 for SQL Server",
            # Evita problemas de certificado en ambientes on-prem
            "extra_params": "Encrypt=yes;TrustServerCertificate=yes;",
        },
        # Para usar la base ya restaurada con --keepdb
        "TEST": {
            "NAME": "test_WorkshopDB",
        },
    }
}

from .settings_flags import *

# Si tus tests usan cache/email/etc. y quieres que no “ensucien” nada, puedes dejar lo que tengas por defecto
