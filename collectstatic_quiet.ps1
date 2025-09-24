param(
  [switch]$Clear = $false
)
$ErrorActionPreference = 'Stop'

# Ensure settings (adjust if you use a different one)
if (-not $env:DJANGO_SETTINGS_MODULE) {
  $env:DJANGO_SETTINGS_MODULE = "workshop.settings_sqlserver"
}

# Build command
$cmd = @("manage.py", "collectstatic", "--noinput", "-v", "0")
if ($Clear) { $cmd += "--clear" }

Write-Host "Running: python $($cmd -join ' ')" -ForegroundColor Cyan

try {
  # Run quietly and suppress stderr output
  & python @cmd 2>$null
  Write-Host "collectstatic (quiet) completed." -ForegroundColor Green
}
catch {
  Write-Host "collectstatic failed." -ForegroundColor Red
  throw
}
