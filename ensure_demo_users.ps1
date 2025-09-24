<#
.SYNOPSIS
  Crea (o actualiza) usuarios de demo para autenticación JWT en la BD activa (según DJANGO_SETTINGS_MODULE).
  - asesor_test / asesor123  (grupo: Asesor)
  - mecanico_test / mecanico123 (grupo: Mecanico)

.EXAMPLE
  # Ejecutar desde backend, con el server corriendo en settings_sqlserver
  powershell -ExecutionPolicy Bypass -File .\ensure_demo_users.ps1
#>

param(
  [string]$DjangoSettings = $env:DJANGO_SETTINGS_MODULE
)

if (-not $DjangoSettings) {
  # Por defecto, usa settings_sqlserver
  $env:DJANGO_SETTINGS_MODULE = "workshop.settings_sqlserver"
  $DjangoSettings = $env:DJANGO_SETTINGS_MODULE
}

Write-Host "Usando settings: $DjangoSettings" -ForegroundColor Cyan

# Activar venv si existe
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
  . .\.venv\Scripts\Activate.ps1
}

# Asegurar que los grupos existan (seed_roles)
python manage.py seed_roles

# Crear/actualizar usuarios de demo
$py = @"
from django.contrib.auth.models import User, Group

def ensure_user(username, password, group_name, is_staff=False, email=None):
    u, _ = User.objects.get_or_create(username=username, defaults={'is_staff': is_staff, 'email': email or f'{username}@local'})
    u.set_password(password)
    u.is_active = True
    u.is_staff = is_staff
    u.save()
    g = Group.objects.get(name=group_name)
    u.groups.add(g)
    print(f'OK: {username} en grupo {group_name}')

ensure_user('asesor_test', 'asesor123', 'Asesor', True, 'asesor@test.local')
ensure_user('mecanico_test', 'mecanico123', 'Mecanico', False, 'meca@test.local')
"@

python manage.py shell -c $py

Write-Host "Listo. Puedes probar login con: asesor_test / asesor123" -ForegroundColor Green
