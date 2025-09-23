param(
  [string]$Server,
  [string]$User,
  [string]$Password,
  [string]$BackupDir = ""   # opcional (ya no se usa si consultamos msdb)
)

# localizar sqlcmd
$Sqlcmd = (Get-Command sqlcmd -ErrorAction SilentlyContinue).Source
if (-not $Sqlcmd) {
  foreach ($c in @(
    "C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\180\Tools\Binn\sqlcmd.exe",
    "C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\sqlcmd.exe",
    "C:\Program Files\Microsoft SQL Server\150\Tools\Binn\sqlcmd.exe"
  )) { if (Test-Path $c) { $Sqlcmd = $c; break } }
}
if (-not $Sqlcmd) { throw "sqlcmd.exe no encontrado" }

# Ãºltimo FULL backup de WorkshopDB (ruta local al motor)
$sql = @"
SET NOCOUNT ON;
SELECT TOP 1 mf.physical_device_name
FROM msdb.dbo.backupset b
JOIN msdb.dbo.backupmediafamily mf ON b.media_set_id = mf.media_set_id
WHERE b.type='D' AND b.database_name='WorkshopDB'
ORDER BY b.backup_start_date DESC;
"@

$bakPath = & $Sqlcmd -S $Server -U $User -P $Password -N -C -h -1 -Q $sql
if (-not $bakPath) { throw "No se encontrÃ³ un FULL backup en msdb para WorkshopDB." }
Write-Host "Usando .bak: $bakPath"

# restaurar a test_WorkshopDB con el script robusto
& (Join-Path $PSScriptRoot 'sql_restore_v3.ps1') `
  -Server $Server `
  -DbName 'test_WorkshopDB' `
  -BakPath $bakPath `
  -User $User -Password $Password -Encrypt -TrustServerCertificate -Quiet
