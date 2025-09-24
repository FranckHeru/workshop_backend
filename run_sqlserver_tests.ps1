<#
.SYNOPSIS
  Orquesta pruebas end-to-end del backend contra SQL Server desde PowerShell.
  - Crea (si no existen) las bases WorkshopDB y test_WorkshopDB en 192.168.3.20\APPSGS
  - Ejecuta migraciones usando el settings de pruebas SQL Server
  - Corre los tests del proyecto (especialmente core/tests/test_rbac_api.py) contra SQL Server

.DESCRIPTION
  Ajusta los parÃ¡metros si tu servidor/credenciales cambian.
  Debes ejecutar este script desde la carpeta: workshop_backend\backend

.PARAMETER ServerInstance
  Instancia/servidor de SQL Server (usa la forma SERVIDOR\INSTANCIA para instancias nombradas)

.PARAMETER User
  Usuario SQL Server

.PARAMETER Password
  Password SQL Server

.PARAMETER DbName
  Nombre de la base principal (no se usa durante tests, pero se crea por conveniencia)

.PARAMETER TestDbName
  Nombre de la base de pruebas que usarÃ¡n los tests

.EXAMPLE
  # Desde workshop_backend\backend
  powershell -ExecutionPolicy Bypass -File .\run_sqlserver_tests.ps1
#>

param(
  [string]$ServerInstance = "192.168.3.20\APPSGS",
  [string]$User = "sa",
  [string]$Password =  [Environment]::GetEnvironmentVariable("WORKSHOP_SQL_SA_PWD","Machine"),
  [string]$DbName = "WorkshopDB",
  [string]$TestDbName = "test_WorkshopDB"
)

function Assert-Exit($Ok, $Msg) {
  if (-not $Ok) {
    Write-Error $Msg
    exit 1
  }
}

# 1) Validaciones mÃ­nimas
Write-Host "== Verificando ubicaciÃ³n (debe existir manage.py) ==" -ForegroundColor Cyan
Assert-Exit (Test-Path ".\manage.py") "Ejecuta este script desde workshop_backend\backend (no se encontrÃ³ manage.py)."

# Intentar activar venv si existe
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
  Write-Host "== Activando entorno virtual .venv ==" -ForegroundColor Cyan
  . .\.venv\Scripts\Activate.ps1
}

# 2) Crear DBs (si faltan)
Write-Host "== Creando bases si no existen en $ServerInstance ==" -ForegroundColor Cyan
$tsqlCreate = @"
IF DB_ID(N'$TestDbName') IS NULL
BEGIN
  PRINT 'Creating $TestDbName...';
  CREATE DATABASE [$TestDbName] COLLATE Modern_Spanish_CI_AS;
END
ELSE
BEGIN
  PRINT '$TestDbName already exists.';
END

IF DB_ID(N'$DbName') IS NULL
BEGIN
  PRINT 'Creating $DbName...';
  CREATE DATABASE [$DbName] COLLATE Modern_Spanish_CI_AS;
END
ELSE
BEGIN
  PRINT '$DbName already exists.';
END
"@

# Requiere sqlcmd instalado (Microsoft ODBC + Command Line Utilities)
$sqlcmd = Get-Command sqlcmd -ErrorAction SilentlyContinue
Assert-Exit $sqlcmd "No se encontrÃ³ 'sqlcmd'. Instala SQL Server Command Line Utilities (MsODBC + sqlcmd)."

& sqlcmd -S $ServerInstance -U $User -P $Password -b -Q $tsqlCreate
Assert-Exit ($LASTEXITCODE -eq 0) "Fallo al crear/verificar las bases en SQL Server."

# 3) Exportar variables para que Django use el settings de pruebas SQL Server
Write-Host "== Configurando DJANGO_SETTINGS_MODULE para pruebas SQL Server ==" -ForegroundColor Cyan
$env:DJANGO_SETTINGS_MODULE = "workshop.test_settings_sqlserver"

# 4) Migraciones contra la BD de pruebas
Write-Host "== Ejecutando migraciones sobre $TestDbName ==" -ForegroundColor Cyan
python --version
Assert-Exit ($LASTEXITCODE -eq 0) "Python no estÃ¡ disponible en PATH."

python manage.py migrate --noinput
Assert-Exit ($LASTEXITCODE -eq 0) "Fallaron las migraciones contra $TestDbName."

# 5) Correr tests (manteniendo la BD para mayor velocidad)
Write-Host "== Ejecutando suite de tests contra SQL Server ==" -ForegroundColor Cyan
python manage.py test core -v 2 --keepdb
$code = $LASTEXITCODE

if ($code -eq 0) {
  Write-Host "âœ… TODOS LOS TESTS PASARON contra SQL Server." -ForegroundColor Green
} else {
  Write-Error "âŒ Algunos tests fallaron. Revisa la salida anterior."
}

exit $code


