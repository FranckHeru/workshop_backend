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
        "$Env:ProgramFiles\Microsoft SQL Server\150\Tools\Binn\sqlcmd.exe"
    )
    foreach ($c in $cands) { if (Test-Path $c) { return $c } }
    $gc = Get-Command sqlcmd -ErrorAction SilentlyContinue
    if ($gc) { return $gc.Source }
    throw "No se encontró sqlcmd.exe. Instala las Command Line Utilities o especifica -SqlcmdPath."
}
$sqlcmd = Resolve-Sqlcmd -PathHint $SqlcmdPath

if (!(Test-Path $BakPath)) { throw "No existe $BakPath (ruta del servidor SQL)." }

$sql = @"
DECLARE @bak nvarchar(4000) = N'$BakPath', @db sysname = N'$DbName';
DECLARE @LogicalData sysname, @LogicalLog sysname;

DECLARE @fl TABLE (
  LogicalName nvarchar(128), PhysicalName nvarchar(260), [Type] char(1), FileGroupName nvarchar(128),
  [Size] numeric(20,0), MaxSize numeric(20,0), FileId int, CreateLSN numeric(25,0), DropLSN numeric(25,0),
  UniqueId uniqueidentifier, ReadOnlyLSN numeric(25,0), ReadWriteLSN numeric(25,0),
  BackupSizeInBytes bigint, SourceBlockSize int, FileGroupId int, LogGroupGUID uniqueidentifier,
  DifferentialBaseLSN numeric(20,0), DifferentialBaseGUID uniqueidentifier,
  IsReadOnly bit, IsPresent bit, TDEThumbprint varbinary(32), SnapshotUrl nvarchar(360)
);
DECLARE @flcmd nvarchar(max) = N'RESTORE FILELISTONLY FROM DISK = N''' + @bak + N'''';
INSERT INTO @fl EXEC(@flcmd);

SELECT TOP(1) @LogicalData = LogicalName FROM @fl WHERE [Type] = 'D';
SELECT TOP(1) @LogicalLog  = LogicalName FROM @fl WHERE [Type] = 'L';

IF @LogicalData IS NULL OR @LogicalLog IS NULL
  THROW 50001, 'No se pudieron detectar nombres lógicos en el .bak', 1;

DECLARE @DataDir nvarchar(4000), @LogDir nvarchar(4000);
SELECT TOP(1) @DataDir = LEFT(physical_name, LEN(physical_name)-CHARINDEX('\', REVERSE(physical_name))+1)
  FROM sys.master_files WHERE database_id = DB_ID('WorkshopDB') AND type_desc='ROWS';
SELECT TOP(1) @LogDir = LEFT(physical_name, LEN(physical_name)-CHARINDEX('\', REVERSE(physical_name))+1)
  FROM sys.master_files WHERE database_id = DB_ID('WorkshopDB') AND type_desc='LOG';

DECLARE @DataFile nvarchar(4000) = @DataDir + @db + N'.mdf';
DECLARE @LogFile  nvarchar(4000) = @LogDir + @db + N'_log.ldf';

IF DB_ID(@db) IS NOT NULL EXEC('ALTER DATABASE [' + @db + '] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;');

DECLARE @cmd nvarchar(max) =
  N'RESTORE DATABASE [' + @db + N'] FROM DISK = N''' + @bak + N''' WITH REPLACE, STATS=10, ' +
  N'MOVE N''' + @LogicalData + N''' TO N''' + @DataFile + N''', ' +
  N'MOVE N''' + @LogicalLog  + N''' TO N''' + @LogFile  + N''', ' +
  N'RECOVERY;';

PRINT @cmd;
EXEC(@cmd);

IF DB_ID(@db) IS NOT NULL EXEC('ALTER DATABASE [' + @db + '] SET MULTI_USER;');
"@

$args = @("-S", $Server, "-Q", $sql)
if ($User) { $args += @("-U", $User, "-P", $Password) }
if ($Encrypt) { $args += "-N" }
if ($TrustServerCertificate) { $args += "-C" }

& $sqlcmd @args
if ($LASTEXITCODE -ne 0) { throw "El restore falló (exitcode $LASTEXITCODE)." }
Write-Host "Restore completado en $DbName" -ForegroundColor Green
