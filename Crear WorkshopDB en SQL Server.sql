-- 1) Crear la base de datos WorkshopDB si no existe
IF DB_ID('WorkshopDB') IS NULL
BEGIN
    CREATE DATABASE WorkshopDB;
    ALTER DATABASE WorkshopDB SET COMPATIBILITY_LEVEL = 150; -- SQL Server 2019
END
GO

-- 2) Crear login exclusivo para la aplicación (recomendado, en vez de usar 'sa')
IF NOT EXISTS (SELECT 1 FROM sys.sql_logins WHERE name = 'workshop_login')
BEGIN
    CREATE LOGIN workshop_login 
        WITH PASSWORD = 'Strong!Pass123', 
             CHECK_POLICY = ON, 
             CHECK_EXPIRATION = OFF;
END
GO

-- 3) Crear usuario dentro de WorkshopDB y darle permisos
USE WorkshopDB;
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'workshop_user')
    CREATE USER workshop_user FOR LOGIN workshop_login;
ALTER ROLE db_owner ADD MEMBER workshop_user;
GO
