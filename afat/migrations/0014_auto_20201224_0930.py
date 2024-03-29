# Generated by Django 3.1.4 on 2020-12-24 09:30

# Django
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("afat", "0013_basic_module_access_permissions"),
    ]

    operations = [
        migrations.AddField(
            model_name="afatlink",
            name="esi_fleet_id",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="afatlink",
            name="is_registered_on_esi",
            field=models.BooleanField(
                default=False,
                help_text="Whether this is an ESI fat link is registered on ESI",
            ),
        ),
    ]
