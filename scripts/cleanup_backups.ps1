param(
  [int]$RetentionDays = 14,
  [string]$Dir      = 'C:\Program Files\Microsoft SQL Server\MSSQL15.APPSGS\MSSQL\Backup',
  [string]$Pattern  = 'WorkshopDB_*.bak',
  [string]$Log      = 'C:\Taller\workshop_backend\backend\logs\backup_cleanup.log'
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
