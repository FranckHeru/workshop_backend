param(
  [string]$Version = "v2.0.0-fase3",
  [string]$OutDir = ".\dist"
)
$ErrorActionPreference = "Stop"

$repo = (Resolve-Path ".").Path
$stage = Join-Path $OutDir ("artifact_" + $Version + "_staging")
$zip   = Join-Path $OutDir ("workshop_backend_" + $Version + ".zip")

if (!(Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
New-Item -ItemType Directory -Force -Path $stage | Out-Null

$rcArgs = @(
  $repo, $stage, "/E",
  "/XD", ".git", ".venv", ".venv_x64", "backups", "logs", "staticfiles", "__pycache__",
  "/XF", "*.pyc", "*.pyo", "*.log"
)
robocopy @rcArgs | Out-Null

if (Test-Path ".\api-schema.yaml") { Copy-Item ".\api-schema.yaml" $stage -Force }

if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zip -Force

$hash = (Get-FileHash $zip -Algorithm SHA256).Hash
Write-Host "Artefacto: $zip" -ForegroundColor Green
Write-Host ("SHA256: " + $hash) -ForegroundColor Green
