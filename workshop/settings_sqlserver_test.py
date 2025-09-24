import os
from .settings_sqlserver import *

DATABASES["default"]["USER"] = os.environ.get("DB_USER", DATABASES["default"].get("USER", "sa"))
DATABASES["default"]["PASSWORD"] = (
    os.environ.get("DB_PASSWORD")
    or os.environ.get("WORKSHOP_SQL_SA_PWD")
    or ""
)
