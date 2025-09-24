<#
.SYNOPSIS
  Smoke tests de la API con PowerShell (sin Postman).
  - Login JWT
  - Listados protegidos
  - Creación básica de customer, vehicle (con owner y plate <=20), y workorder (con number)
#>
param(
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [string]$Username = "asesor_test",
  [string]$Password = "asesor123"
)

function Assert-Exit($Cond, $Msg) { if (-not $Cond) { Write-Error $Msg; exit 1 } }

function Invoke-Json {
  param([string]$Method,[string]$Url,[Hashtable]$Headers,[Hashtable]$Body,[switch]$Quiet)
  $params = @{ Method=$Method; Uri=$Url; Headers=$Headers; ErrorAction='Stop' }
  if ($Body) { $params['ContentType']='application/json'; $params['Body']=($Body | ConvertTo-Json -Depth 6) }
  try {
    $resp = Invoke-RestMethod @params
    if (-not $Quiet) { Write-Host ("{0} {1} => OK" -f $Method, $Url) -ForegroundColor Green; $resp | ConvertTo-Json -Depth 6 }
    return $resp
  } catch {
    Write-Host ("{0} {1} => ERROR" -f $Method, $Url) -ForegroundColor Red
    if ($_.Exception.Response) {
      try { $stream=$_.Exception.Response.GetResponseStream(); $reader=New-Object System.IO.StreamReader($stream); $text=$reader.ReadToEnd(); Write-Host $text } catch {}
    } else { Write-Host $_.Exception.Message }
    throw
  }
}

# Pre-check: verify server is reachable
try {
  $uri = [System.Uri]$BaseUrl
  $apiHost = $uri.Host
  $apiPort = if ($uri.Port -gt 0) { $uri.Port } else { if ($uri.Scheme -eq 'https') {443} else {80} }
  Write-Host ("== Verificando API en {0}:{1} ==" -f $apiHost, $apiPort) -ForegroundColor Cyan
  $tcp = Test-NetConnection -ComputerName $apiHost -Port $apiPort -InformationLevel Quiet
  if (-not $tcp) {
    Write-Error ("No se puede conectar a {0}:{1}. ¿Levantaste el servidor Django? Ejecuta:`n" +
      ".\.venv\Scripts\Activate.ps1;`n" +
      "$env:DJANGO_SETTINGS_MODULE='workshop.settings_sqlserver';`n" +
      "python manage.py migrate --noinput;`n" +
      "python manage.py seed_roles;`n" +
      "python manage.py runserver 0.0.0.0:8000") -ErrorAction Stop
  }
} catch { Write-Warning "No se pudo validar conectividad previa. Continuando..." }

# 1) Login
Write-Host "== AUTH: JWT create ==" -ForegroundColor Cyan
$login = Invoke-Json -Method 'POST' -Url "$BaseUrl/api/auth/jwt/create/" -Headers @{} -Body @{ username=$Username; password=$Password } -Quiet
$access = $login.access; $refresh = $login.refresh
Assert-Exit ($access -and $refresh) "No se obtuvo token JWT."
$H = @{ Authorization = "Bearer $access" }

# 2) Listas
Write-Host "== GET: customers, vehicles, services, parts, workorders ==" -ForegroundColor Cyan
Invoke-Json -Method 'GET' -Url "$BaseUrl/api/customers/"  -Headers $H -Quiet
Invoke-Json -Method 'GET' -Url "$BaseUrl/api/vehicles/"   -Headers $H -Quiet
Invoke-Json -Method 'GET' -Url "$BaseUrl/api/services/"   -Headers $H -Quiet
Invoke-Json -Method 'GET' -Url "$BaseUrl/api/parts/"      -Headers $H -Quiet
Invoke-Json -Method 'GET' -Url "$BaseUrl/api/workorders/" -Headers $H -Quiet

# 3) Crear customer y vehicle
Write-Host "== POST: crear customer y vehicle demo ==" -ForegroundColor Cyan
$now = Get-Date -Format "yyMMddHHmmss"
$customer = Invoke-Json -Method 'POST' -Url "$BaseUrl/api/customers/" -Headers $H -Body @{ name="Cliente Smoke PS"; email="psmoke@example.com"; phone="7000-0000" } -Quiet
$customerId = $customer.id; Assert-Exit $customerId "No se pudo crear customer."
$vehicle = Invoke-Json -Method 'POST' -Url "$BaseUrl/api/vehicles/" -Headers $H -Body @{ plate=("PS"+$now); brand="Toyota"; model="Hilux"; year=2021; owner=$customerId } -Quiet
$vehicleId = $vehicle.id; Assert-Exit $vehicleId "No se pudo crear vehicle."

# 4) Crear workorder (número requerido)
Write-Host "== POST: crear workorder demo ==" -ForegroundColor Cyan
$woNumber = "WO-$now"
$workorder = Invoke-Json -Method 'POST' -Url "$BaseUrl/api/workorders/" -Headers $H -Body @{ number=$woNumber; customer=$customerId; vehicle=$vehicleId; status="OPEN"; notes=("Smoke test "+$now) } -Quiet
$workorderId = $workorder.id; Assert-Exit $workorderId "No se pudo crear workorder."

Write-Host ""; Write-Host ("✅ Smoke OK: customer={0} vehicle={1}(PS{2}) workorder={3} number={4}" -f $customerId, $vehicleId, $now, $workorderId, $woNumber) -ForegroundColor Green