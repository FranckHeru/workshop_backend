<# setup_backup_jobs.ps1
Crea/actualiza:
  - Workshop Backup Full (daily)    -> 01:30
  - Workshop Backup Cleanup (daily) -> 02:15
  - Workshop Restore Smoke (weekly) -> Domingos 03:00
#>

# --- Consola/UTF-8 (evita mojibake en PS 5.1) ---
try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false) } catch {}

$ErrorActionPreference = 'Stop'

# --- PARÁMETROS BASE ---
$RepoRoot   = 'C:\Taller\workshop_backend\backend'
$ScriptsDir = Join-Path $RepoRoot 'scripts'
$LogsDir    = Join-Path $RepoRoot 'logs'
$BackupDir  = 'C:\Program Files\Microsoft SQL Server\MSSQL15.APPSGS\MSSQL\Backup'

$Server   = 'tcp:192.168.3.20,50222'
$DbName   = 'WorkshopDB'
$User     = 'sa'
[Environment]::GetEnvironmentVariable('WORKSHOP_SQL_SA_PWD','Machine')   # ← según pediste

# Rutas de scripts existentes
$BackupScript  = Join-Path $ScriptsDir 'sql_backup_v2.ps1'   # ya lo tienes
$RestoreScript = Join-Path $ScriptsDir 'sql_restore_v3.ps1'  # ya lo tienes

# Rutas de scripts que crearemos si no existen
$CleanupScript = Join-Path $ScriptsDir 'cleanup_backups.ps1'
$SmokeScript   = Join-Path $ScriptsDir 'restore_smoke.ps1'

# --- PREP ENTORNO ---
New-Item -ItemType Directory -Force -Path $ScriptsDir | Out-Null
New-Item -ItemType Directory -Force -Path $LogsDir    | Out-Null

if (-not (Test-Path $BackupScript))  { throw "No existe $BackupScript" }
if (-not (Test-Path $RestoreScript)) { throw "No existe $RestoreScript" }

# --- CREAR cleanup_backups.ps1 si falta ---
if (-not (Test-Path $CleanupScript)) {
@'
param(
  [int]$RetentionDays = 14,
  [string]$Dir      = "C:\Program Files\Microsoft SQL Server\MSSQL15.APPSGS\MSSQL\Backup",
  [string]$Pattern  = "WorkshopDB_*.bak",
  [string]$Log      = "C:\Taller\workshop_backend\backend\logs\backup_cleanup.log"
)
New-Item -ItemType Directory -Force -Path (Split-Path $Log) | Out-Null
$now = Get-Date
$cut = $now.AddDays(-$RetentionDays)
$events = @()

Get-ChildItem -Path $Dir -Filter $Pattern -File -ErrorAction SilentlyContinue |
  Where-Object { $_.LastWriteTime -lt $cut } |
  ForEach-Object {
    try {
      $info = '{0:u} DELETE {1} {2:n0} bytes (lastwrite {3:u})' -f $now,$_.FullName,$_.Length,$_.LastWriteTime
      Remove-Item -LiteralPath $_.FullName -Force
      $events += $info
    } catch {
      $events += ('{0:u} ERROR deleting {1}: {2}' -f $now,$_.FullName,$_.Exception.Message)
    }
  }

if (-not $events) { $events = @('{0:u} NOOP nothing older than {1}d' -f $now,$RetentionDays) }
$events | Add-Content -Path $Log -Encoding UTF8
exit 0
'@ | Set-Content -Path $CleanupScript -Encoding UTF8
}

# --- CREAR restore_smoke.ps1 si falta ---
if (-not (Test-Path $SmokeScript)) {
@"
param(
  [string]$Server    = "$Server",
  [string]$User      = "$User",
  [string]$Password  =  [Environment]::GetEnvironmentVariable("WORKSHOP_SQL_SA_PWD","Machine"),
  [string]$BackupDir = "$BackupDir"
)
\$latest = Get-ChildItem -Path \$BackupDir -Filter 'WorkshopDB_*.bak' -File |
           Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not \$latest) { Write-Error "No .bak found in \$BackupDir"; exit 1 }

& "$RestoreScript" `
  -Server \$Server `
  -DbName 'test_WorkshopDB' `
  -BakPath \$latest.FullName `
  -User \$User -Password \$Password -Encrypt -TrustServerCertificate -Quiet
"@ | Set-Content -Path $SmokeScript -Encoding UTF8
}

# --- HELPERS ---
function Register-ReplaceTask {
  param([string]$Name,[Microsoft.Management.Infrastructure.CimInstance]$Action,
        [Microsoft.Management.Infrastructure.CimInstance]$Trigger,
        [Microsoft.Management.Infrastructure.CimInstance]$Principal)

  $existing = Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue
  if ($existing) { Unregister-ScheduledTask -TaskName $Name -Confirm:$false }
  Register-ScheduledTask -TaskName $Name -Action $Action -Trigger $Trigger -Principal $Principal | Out-Null
}

# Principal SYSTEM
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -RunLevel Highest

# --- TAREA 1: Backup diario 01:30 ---
$backupArgs = @(
  '-NoProfile','-ExecutionPolicy','Bypass','-File',"`"$BackupScript`"",
  '-Server', "`"$Server`"",
  '-DbName', "`"$DbName`"",
  '-User', "`"$User`"",
  '-Password', "`"$Password`"",
  '-Encrypt','-TrustServerCertificate',
  '-OutDir', "`"$BackupDir`""
) -join ' '

$backupAction  = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $backupArgs
$backupTrigger = New-ScheduledTaskTrigger -Daily -At 1:30am
Register-ReplaceTask -Name 'Workshop Backup Full (daily)' -Action $backupAction -Trigger $backupTrigger -Principal $principal

# --- TAREA 2: Cleanup diario 02:15 ---
$cleanupLog  = Join-Path $LogsDir 'backup_cleanup.log'
$cleanupArgs = @(
  '-NoProfile','-ExecutionPolicy','Bypass','-File',"`"$CleanupScript`"",
  '-RetentionDays','14',
  '-Dir', "`"$BackupDir`"",
  '-Pattern', "`"WorkshopDB_*.bak`"",
  '-Log', "`"$cleanupLog`""
) -join ' '

$cleanupAction  = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $cleanupArgs
$cleanupTrigger = New-ScheduledTaskTrigger -Daily -At 2:15am
Register-ReplaceTask -Name 'Workshop Backup Cleanup (daily)' -Action $cleanupAction -Trigger $cleanupTrigger -Principal $principal

# --- TAREA 3: Restore smoke semanal (Dom 03:00) ---
$smokeArgs = @(
  '-NoProfile','-ExecutionPolicy','Bypass','-File',"`"$SmokeScript`"",
  '-Server', "`"$Server`"",
  '-User', "`"$User`"",
  '-Password', "`"$Password`"",
  '-BackupDir', "`"$BackupDir`""
) -join ' '

$smokeAction  = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $smokeArgs
$smokeTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3:00am
Register-ReplaceTask -Name 'Workshop Restore Smoke (weekly)' -Action $smokeAction -Trigger $smokeTrigger -Principal $principal

# --- PRUEBA INMEDIATA DEL BACKUP ---
Write-Host "Lanzando prueba inmediata del backup..."
Start-ScheduledTask -TaskName 'Workshop Backup Full (daily)'
Start-Sleep -Seconds 6
$info = Get-ScheduledTaskInfo -TaskName 'Workshop Backup Full (daily)'
("{0}  LastRunTime={1}  LastTaskResult={2}" -f $info.TaskName,$info.LastRunTime,$info.LastTaskResult) | Write-Host

# Mostrar último .bak (evita ${var}:)
Write-Host ('Último .bak en {0}:' -f $BackupDir)
Get-ChildItem -Path (Join-Path $BackupDir 'WorkshopDB_*.bak') -File -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1 Name,Length,LastWriteTime |
  Format-Table -AutoSize


