# Generated by Django 4.0.10 on 2023-09-22 08:15

# Django
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("eveonline", "0017_alliance_and_corp_names_are_not_unique"),
        ("afat", "0022_afatlink_esi_error_count"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AFat",
            new_name="Fat",
        ),
    ]
