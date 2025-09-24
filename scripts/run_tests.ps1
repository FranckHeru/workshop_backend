param(
  [string]$VenvPath = ".\.venv_x64",
  [string]$Settings = "workshop.settings_prod"
)
$ErrorActionPreference = "Stop"
$python = Join-Path $VenvPath "Scripts\python.exe"
if (!(Test-Path $python)) { throw "Python no encontrado en $VenvPath" }
$env:DJANGO_SETTINGS_MODULE = $Settings
& $python manage.py test --verbosity 2
