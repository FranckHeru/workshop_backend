# catalog/migrations/0002_service_part.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("code", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=200)),
                ("price", models.DecimalField(max_digits=10, decimal_places=2, default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Part",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("sku", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=200)),
                ("price", models.DecimalField(max_digits=10, decimal_places=2, default=0)),
                ("stock", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
    ]
