# Generated by Django 3.1.1 on 2020-10-03 22:22

# Django
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("afat", "0010_permissoins_update_20201002_1909"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="manualafat",
            options={
                "verbose_name": "Manual FAT Log",
                "verbose_name_plural": "Manual FAT Logs",
            },
        ),
    ]
