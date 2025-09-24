from .settings_sqlserver import *
import os
DATABASES["default"]["NAME"]     = os.getenv("DB_NAME", "test_WorkshopDB")
DATABASES["default"]["USER"]     = os.getenv("DB_USER", "sa")
DATABASES["default"]["PASSWORD"] = os.getenv("DB_PASSWORD", "")
DATABASES["default"]["HOST"]     = os.getenv("DB_HOST", "192.168.3.20")
DATABASES["default"]["PORT"]     = os.getenv("DB_PORT", "50222")
DATABASES["default"]["OPTIONS"]["driver"] = os.getenv("ODBC_DRIVER","ODBC Driver 18 for SQL Server")
DATABASES["default"]["OPTIONS"]["extra_params"] = os.getenv("MSSQL_EXTRA","TrustServerCertificate=yes;Encrypt=no;")
