# Generated by Django 4.0.10 on 2023-09-22 08:44

# Django
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("afat", "0025_rename_afatlinktype_fleettype"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="fleettype",
            options={
                "default_permissions": (),
                "verbose_name": "Fleet type",
                "verbose_name_plural": "Fleet types",
            },
        ),
        migrations.AlterField(
            model_name="fleettype",
            name="name",
            field=models.CharField(
                help_text="Descriptive name of the fleet type", max_length=254
            ),
        ),
    ]
