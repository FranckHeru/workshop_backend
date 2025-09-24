# run_api_test.ps1
Set-Location C:\Taller\workshop_backend\backend

# Activa venv si no está activo
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    & .\.venv\Scripts\Activate.ps1
} else {
    try { python --version | Out-Null } catch { & .\.venv\Scripts\Activate.ps1 }
}

$env:DJANGO_SETTINGS_MODULE = "workshop.settings_sqlserver_test"

# Migraciones a test_WorkshopDB
python manage.py migrate

# Carga/actualiza roles, opcional pero recomendado si tienes el comando
try { python manage.py seed_roles } catch {}

# Recoge estáticos (para logo/css Jazzmin)
python manage.py collectstatic --noinput

Write-Host "Iniciando server en http://127.0.0.1:8000 con DB test_WorkshopDB..." -ForegroundColor Cyan
python manage.py runserver
