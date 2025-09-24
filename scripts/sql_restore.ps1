param(
    [string]$Server = "localhost",
    [string]$DbName = "test_WorkshopDB",
    [string]$BakPath
)
$ErrorActionPreference = "Stop"
if (!(Test-Path $BakPath)) { throw "No existe " + $BakPath }
$sql = @"
ALTER DATABASE [$DbName] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
RESTORE DATABASE [$DbName]
FROM DISK = N'$BakPath'
WITH REPLACE, RECOVERY, STATS = 10;
ALTER DATABASE [$DbName] SET MULTI_USER;
"@
sqlcmd -S $Server -Q $sql
Write-Host ("Restore completado en " + $DbName) -ForegroundColor Green
