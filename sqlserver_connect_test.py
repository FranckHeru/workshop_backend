# sqlserver_connect_test.py (ajuste)
import os, sys, pyodbc
driver = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 18 for SQL Server")
host   = os.getenv("SQLSERVER_HOST", "localhost")
port   = os.getenv("SQLSERVER_PORT", "")     # <-- DEFAULT VACÍO
db     = os.getenv("SQLSERVER_DB", "WorkshopDB")
user   = os.getenv("SQLSERVER_USER", "sa")
pwd    = os.getenv("SQLSERVER_PASSWORD", "")
extra  = os.getenv("SQLSERVER_EXTRA", "Encrypt=yes;TrustServerCertificate=yes;")

server = f"{host},{port}" if port else host  # si no hay puerto, NO agrega ,1433
conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={db};UID={user};PWD={pwd};{extra}"
print("Connection string =>", conn_str.replace(pwd, "***"))
print("pyodbc drivers  =>", pyodbc.drivers())
# ... resto igual
