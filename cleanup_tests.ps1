# cleanup_tests.ps1
# Limpia tests del repo (NO toca .venv / .venv_x64 / site-packages) y preserva una lista blanca.
param(
  [string]$Root = (Get-Location).Path
)

Write-Host "Root: $Root" -ForegroundColor Cyan

function Resolve-ExistingPath([string]$p) {
  if ([string]::IsNullOrWhiteSpace($p)) { return $null }
  if (Test-Path -LiteralPath $p) {
    try {
      return (Resolve-Path -LiteralPath $p).Path
    } catch { return $null }
  }
  return $null
}

# 1) Lista blanca (ajusta si cambian tus rutas/archivos)
$keepRaw = @(
  "backend\conftest.py",
  "backend\tests\test_permissions_quotes.py",
  "backend\quotes\tests\test_quotations_api.py"
)
$Keep = @()
foreach ($k in $keepRaw) {
  $abs = Join-Path $Root $k
  $rp = Resolve-ExistingPath $abs
  if ($rp) { $Keep += $rp }
}

# 2) Candidatos a borrar: test_*.py o tests.py FUERA de .venv, .venv_x64 y site-packages
$Candidates = Get-ChildItem -Path $Root -Recurse -File -Include 'test_*.py','tests.py' |
  Where-Object {
    ($_.FullName -notmatch '\\\.venv(\\|$)') -and
    ($_.FullName -notmatch '\\\.venv_x64(\\|$)') -and
    ($_.FullName -notmatch '\\site-packages(\\|$)')
  }

# 3) Excluir la lista blanca
$ToDelete = @()
foreach ($c in $Candidates) {
  $isKeep = $false
  foreach ($k in $Keep) {
    if ($k -and ($c.FullName -ieq $k)) { $isKeep = $true; break }
  }
  if (-not $isKeep) { $ToDelete += $c }
}

Write-Host "=== DRY RUN: archivos que se borrarían ===" -ForegroundColor Yellow
if ($ToDelete.Count -eq 0) {
  Write-Host "No hay nada que borrar. ✅" -ForegroundColor Green
  exit 0
}
$ToDelete | ForEach-Object { Write-Host $_.FullName }

$ans = Read-Host "¿Borrar estos $($ToDelete.Count) archivo(s)? (y/n)"
if ($ans -match '^(y|s)$') {
  foreach ($f in $ToDelete) {
    try { Remove-Item -Force -LiteralPath $f.FullName } catch { Write-Host "No se pudo borrar: $($f.FullName)" -ForegroundColor Red }
  }
  Write-Host "Listo: archivos borrados. ✅" -ForegroundColor Green
} else {
  Write-Host "Cancelado. No se borró nada." -ForegroundColor DarkYellow
}
