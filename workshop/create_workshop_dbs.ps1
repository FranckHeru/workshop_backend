# create_workshop_dbs.ps1
$server = "192.168.3.20\APPSGS"
$user   = "sa"
$pass   =  [Environment]::GetEnvironmentVariable("WORKSHOP_SQL_SA_PWD","Machine")

# Crea DB de pruebas
sqlcmd -S $server -U $user -P $pass -b -Q @"
IF DB_ID('test_WorkshopDB') IS NULL
BEGIN
    PRINT 'Creating test_WorkshopDB...';
    CREATE DATABASE [test_WorkshopDB]
    COLLATE Modern_Spanish_CI_AS;
END
ELSE
BEGIN
    PRINT 'test_WorkshopDB already exists.';
END
"@

# Crea DB de producciÃ³n (si quieres crearla ya)
sqlcmd -S $server -U $user -P $pass -b -Q @"
IF DB_ID('WorkshopDB') IS NULL
BEGIN
    PRINT 'Creating WorkshopDB...';
    CREATE DATABASE [WorkshopDB]
    COLLATE Modern_Spanish_CI_AS;
END
ELSE
BEGIN
    PRINT 'WorkshopDB already exists.';
END
"@


