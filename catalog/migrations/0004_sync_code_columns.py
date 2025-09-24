from django.db import migrations

SERVICE_CODE_LEN = 50
PART_CODE_LEN = 50

ADD_CODE_SERVICE_SQL = f"""
IF COL_LENGTH('dbo.catalog_service', 'code') IS NULL
BEGIN
    ALTER TABLE [dbo].[catalog_service] ADD [code] NVARCHAR({SERVICE_CODE_LEN}) NULL;
END;

IF COL_LENGTH('dbo.catalog_service', 'code') IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'uq_catalog_service_code_notnull'
      AND object_id = OBJECT_ID('dbo.catalog_service')
)
BEGIN
    DECLARE @sql NVARCHAR(MAX) =
        N'CREATE UNIQUE INDEX [uq_catalog_service_code_notnull]
           ON [dbo].[catalog_service]([code])
           WHERE [code] IS NOT NULL;';
    EXEC sp_executesql @sql;
END;
"""

DROP_CODE_SERVICE_SQL = """
IF EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'uq_catalog_service_code_notnull'
      AND object_id = OBJECT_ID('dbo.catalog_service')
)
BEGIN
    DECLARE @sql1 NVARCHAR(MAX) =
        N'DROP INDEX [uq_catalog_service_code_notnull] ON [dbo].[catalog_service];';
    EXEC sp_executesql @sql1;
END;

IF COL_LENGTH('dbo.catalog_service', 'code') IS NOT NULL
BEGIN
    ALTER TABLE [dbo].[catalog_service] DROP COLUMN [code];
END;
"""

ADD_CODE_PART_SQL = f"""
IF COL_LENGTH('dbo.catalog_part', 'code') IS NULL
BEGIN
    ALTER TABLE [dbo].[catalog_part] ADD [code] NVARCHAR({PART_CODE_LEN}) NULL;
END;

IF COL_LENGTH('dbo.catalog_part', 'code') IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'uq_catalog_part_code_notnull'
      AND object_id = OBJECT_ID('dbo.catalog_part')
)
BEGIN
    DECLARE @sql NVARCHAR(MAX) =
        N'CREATE UNIQUE INDEX [uq_catalog_part_code_notnull]
           ON [dbo].[catalog_part]([code])
           WHERE [code] IS NOT NULL;';
    EXEC sp_executesql @sql;
END;
"""

DROP_CODE_PART_SQL = """
IF EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'uq_catalog_part_code_notnull'
      AND object_id = OBJECT_ID('dbo.catalog_part')
)
BEGIN
    DECLARE @sql1 NVARCHAR(MAX) =
        N'DROP INDEX [uq_catalog_part_code_notnull] ON [dbo].[catalog_part];';
    EXEC sp_executesql @sql1;
END;

IF COL_LENGTH('dbo.catalog_part', 'code') IS NOT NULL
BEGIN
    ALTER TABLE [dbo].[catalog_part] DROP COLUMN [code];
END;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0003_add_code_to_service_part"),
    ]

    operations = [
        migrations.RunSQL(
            sql=ADD_CODE_SERVICE_SQL,
            reverse_sql=DROP_CODE_SERVICE_SQL,
            state_operations=[],
        ),
        migrations.RunSQL(
            sql=ADD_CODE_PART_SQL,
            reverse_sql=DROP_CODE_PART_SQL,
            state_operations=[],
        ),
    ]
