param(
    [string]$Server = "localhost",
    [string]$DbName = "WorkshopDB",
    [string]$OutDir = ".\backups"
)
$ErrorActionPreference = "Stop"
if (!(Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$bak = Join-Path $OutDir ($DbName + "_" + $ts + ".bak")
$sql = @"
BACKUP DATABASE [$DbName]
TO DISK = N'$bak'
WITH NOFORMAT, NOINIT, NAME = N'$DbName-Full', SKIP, NOREWIND, NOUNLOAD, STATS = 10;
"@
sqlcmd -S $Server -Q $sql
Write-Host ("Backup creado: " + $bak) -ForegroundColor Green
