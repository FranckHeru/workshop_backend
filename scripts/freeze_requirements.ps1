param(
    [string]$VenvPath = ".\.venv_x64",
    [string]$OutFile = "requirements-freeze.txt"
)
$ErrorActionPreference = "Stop"
$pip = Join-Path $VenvPath "Scripts\pip.exe"
if (Test-Path $pip) {
    & $pip freeze | Out-File -Encoding utf8 $OutFile
} else {
    $python = Join-Path $VenvPath "Scripts\python.exe"
    if (!(Test-Path $python)) { throw "No se encontró pip ni python en $VenvPath" }
    & $python -m pip freeze | Out-File -Encoding utf8 $OutFile
}
Write-Host "Generado $OutFile" -ForegroundColor Green
