# run_api_prod.ps1
Set-Location C:\Taller\workshop_backend\backend

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    & .\.venv\Scripts\Activate.ps1
} else {
    try { python --version | Out-Null } catch { & .\.venv\Scripts\Activate.ps1 }
}

$env:DJANGO_SETTINGS_MODULE = "workshop.settings_sqlserver_prod"

python manage.py migrate
try { python manage.py seed_roles } catch {}
python manage.py collectstatic --noinput

Write-Host "Iniciando server (NO para producción real) en http://127.0.0.1:8000 con DB WorkshopDB..." -ForegroundColor Yellow
python manage.py runserver
