from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_sync_code_columns'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='service',
                    name='code',
                    field=models.CharField(max_length=50, null=True, blank=True, db_index=True),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "IF COL_LENGTH('catalog_service','code') IS NULL "
                        "ALTER TABLE [catalog_service] ADD [code] NVARCHAR(50) NULL;"
                    ),
                    reverse_sql=(
                        "IF COL_LENGTH('catalog_service','code') IS NOT NULL "
                        "ALTER TABLE [catalog_service] DROP COLUMN [code];"
                    ),
                ),
            ],
        ),
    ]