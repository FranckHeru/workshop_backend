from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_pre_state_code'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='part',
                    name='code',
                    field=models.CharField(max_length=50, null=True, blank=True, db_index=True),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "IF COL_LENGTH('catalog_part','code') IS NULL "
                        "ALTER TABLE [catalog_part] ADD [code] NVARCHAR(50) NULL;"
                    ),
                    reverse_sql=(
                        "IF COL_LENGTH('catalog_part','code') IS NOT NULL "
                        "ALTER TABLE [catalog_part] DROP COLUMN [code];"
                    ),
                ),
            ],
        ),
    ]