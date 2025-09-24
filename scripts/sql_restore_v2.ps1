param(
    [string]$Server = "tcp:localhost,1433",
    [string]$DbName = "test_WorkshopDB",
    [string]$BakPath,
    [string]$User = "",
    [string]$Password = "",
    [switch]$Encrypt = $true,
    [switch]$TrustServerCertificate = $true,
    [string]$SqlcmdPath = ""
)
$ErrorActionPreference = "Stop"

function Resolve-Sqlcmd {
    param([string]$PathHint)
    if ($PathHint -and (Test-Path $PathHint)) { return $PathHint }
    $cands = @(
        "$Env:ProgramFiles\Microsoft SQL Server\Client SDK\ODBC\180\Tools\Binn\sqlcmd.exe",
        "$Env:ProgramFiles\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\sqlcmd.exe",
        "$Env:ProgramFiles\Microsoft SQL Server\Client SDK\ODBC\160\Tools\Binn\sqlcmd.exe",
        "$Env:ProgramFiles\Microsoft SQL Server\Client SDK\ODBC\150\Tools\Binn\sqlcmd.exe"
    )
    foreach ($c in $cands) { if (Test-Path $c) { return $c } }
    $gc = Get-Command sqlcmd -ErrorAction SilentlyContinue
    if ($gc) { return $gc.Source }
    throw "No se encontró sqlcmd.exe. Instala las Command Line Utilities o especifica -SqlcmdPath."
}
$sqlcmd = Resolve-Sqlcmd -PathHint $SqlcmdPath

if (!(Test-Path $BakPath)) { throw "No existe $BakPath" }

$sql = @"
IF DB_ID('$DbName') IS NULL
BEGIN
    PRINT 'Creando base de datos $DbName...';
    DECLARE @cmd nvarchar(max) = 'CREATE DATABASE [$DbName]';
    EXEC(@cmd);
END;
ALTER DATABASE [$DbName] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
RESTORE DATABASE [$DbName]
FROM DISK = N'$BakPath'
WITH REPLACE, RECOVERY, STATS = 10;
ALTER DATABASE [$DbName] SET MULTI_USER;
"@

$args = @("-S", $Server, "-Q", $sql)
if ($User) { $args += @("-U", $User, "-P", $Password) }
if ($Encrypt) { $args += "-N" }
if ($TrustServerCertificate) { $args += "-C" }

& $sqlcmd @args
if ($LASTEXITCODE -ne 0) {
    throw "El restore falló (exitcode $LASTEXITCODE). Revisa el mensaje anterior."
}
Write-Host "Restore completado en $DbName" -ForegroundColor Green
