param(
    [string]$Server = "tcp:localhost,1433",
    [string]$DbName = "WorkshopDB",
    [string]$OutDir = ".\backups",
    [string]$User = "",
    [string]$Password = "",
    [switch]$Encrypt = $true,                # -N
    [switch]$TrustServerCertificate = $true, # -C
    [string]$SqlcmdPath = ""                 # opcional: ruta específica a sqlcmd.exe (v18)
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

if (!(Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$bak = Join-Path $OutDir ($DbName + "_" + $ts + ".bak")

$sql = @"
BACKUP DATABASE [$DbName]
TO DISK = N'$bak'
WITH NOFORMAT, NOINIT, NAME = N'$DbName-Full', SKIP, NOREWIND, NOUNLOAD, STATS = 10;
"@

$args = @("-S", $Server, "-Q", $sql)
if ($User) { $args += @("-U", $User, "-P", $Password) }
if ($Encrypt) { $args += "-N" }
if ($TrustServerCertificate) { $args += "-C" }

& $sqlcmd @args
if ($LASTEXITCODE -ne 0) {
    throw "El backup falló (exitcode $LASTEXITCODE). Revisa el mensaje anterior."
}
Write-Host "Backup creado: $bak" -ForegroundColor Green
