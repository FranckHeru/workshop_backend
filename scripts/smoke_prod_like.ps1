param(
    [string]$VenvPath = ".\.venv_x64",
    [string]$Settings = "workshop.settings_prod"
)
$ErrorActionPreference = "Stop"
$python = Join-Path $VenvPath "Scripts\python.exe"
if (!(Test-Path $python)) { throw "Python no encontrado en $VenvPath" }

$env:DJANGO_SETTINGS_MODULE = $Settings

# Checks de despliegue y migraciones
& $python manage.py check --deploy
& $python manage.py migrate --check

# Collectstatic sin intervención
& $python manage.py collectstatic --noinput

# Generar esquema OpenAPI
& $python manage.py spectacular --file api-schema.yaml

Write-Host "Smoke test prod-like OK" -ForegroundColor Green
