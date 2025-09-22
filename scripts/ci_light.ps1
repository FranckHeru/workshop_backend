param(
  [string]$Version = "v2.0.0-fase3",
  [string]$OutDir = ".\dist"
)
$ErrorActionPreference = "Stop"
$python = ".\.venv_x64\Scripts\python.exe"

try { & ruff --version | Out-Null; if ($LASTEXITCODE) { throw "" } ; & ruff check . } catch { Write-Host "ruff no encontrado, saltando lint." -ForegroundColor Yellow }

$env:DJANGO_SETTINGS_MODULE = "workshop.settings_test"
$env:SECURE_SSL_REDIRECT = "0"
$env:SECURE_HSTS_SECONDS = "0"
$env:SESSION_COOKIE_SECURE = "0"
$env:CSRF_COOKIE_SECURE = "0"
$env:DJANGO_ALLOWED_HOSTS = "testserver,localhost,127.0.0.1"
& $python manage.py test --verbosity 2 --keepdb

$env:DJANGO_SETTINGS_MODULE = "workshop.settings_prod"
& $python manage.py spectacular --file api-schema.yaml

.\scripts\pack_artifact.ps1 -Version $Version -OutDir $OutDir
