# env_sqlserver_example.ps1
# Carga variables de entorno para SQL Server en la sesión actual de PowerShell.
# Uso:
#   cd C:\Taller\workshop_backend\backend
#   . .\env_sqlserver_example.ps1   # (punto espacio al inicio: dot-source)

$env:SQLSERVER_DB = "WorkshopDB"
$env:SQLSERVER_USER = "workshop_user"
$env:SQLSERVER_PASSWORD = "YourPass123!"

# Si usas instancia por IP/PUERTO:
$env:SQLSERVER_HOST = "localhost"
$env:SQLSERVER_PORT = "1433"

# Si usas instancia nombrada, alternativa:
# $env:SQLSERVER_HOST = "192.168.3.20\APPSGS"
# $env:SQLSERVER_PORT = ""  # dejar vacío y permitir SQL Browser, o usa el puerto directo de esa instancia

# Driver ODBC (verifica con: python -c "import pyodbc; print(pyodbc.drivers())")
$env:SQLSERVER_DRIVER = "ODBC Driver 18 for SQL Server"

# Flags de conexión (dev)
$env:SQLSERVER_EXTRA = "Encrypt=no;TrustServerCertificate=yes;"
