param(
  [string]$RepoRoot = ".",
  [string]$TargetDep = "('catalog', '0005a_pre_state_part_code')"
)
$ErrorActionPreference = "Stop"
$glob = Join-Path $RepoRoot "catalog\migrations\0005_*and_more*.py"
$files = Get-ChildItem $glob -ErrorAction SilentlyContinue
if ($files.Count -eq 0) {
  # fallback: any 0005*.py
  $glob = Join-Path $RepoRoot "catalog\migrations\0005*.py"
  $files = Get-ChildItem $glob -ErrorAction SilentlyContinue
}
if ($files.Count -eq 0) { throw "No se encontró el archivo 0005 de catalog." }
$path = $files[0].FullName
$content = Get-Content $path -Raw

# Reemplaza la dependencia a 0004/0005_pre_state_code por 0005a_pre_state_part_code
$content = $content -replace "\('catalog'\s*,\s*'0004_sync_code_columns'\)", $TargetDep
$content = $content -replace "\('catalog'\s*,\s*'0005_pre_state_code'\)", $TargetDep

Set-Content -Path $path -Value $content -Encoding UTF8
Write-Host "Patched dependency in: $path -> depends on catalog.0005a_pre_state_part_code" -ForegroundColor Green
