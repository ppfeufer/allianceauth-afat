# Generated by Django 4.2.16 on 2024-11-08 16:42

# Django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("afat", "0023_the_big_rename"),
    ]

    operations = [
        migrations.CreateModel(
            name="Doctrine",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Short name to identify this doctrine",
                        max_length=255,
                        unique=True,
                        verbose_name="Name",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="You can add notes about this doctrine here if you want. (optional)",
                        verbose_name="Notes",
                    ),
                ),
                (
                    "is_enabled",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="Whether this doctrine is enabled or not.",
                        verbose_name="Is enabled",
                    ),
                ),
            ],
            options={
                "verbose_name": "Doctrine",
                "verbose_name_plural": "Doctrines",
                "default_permissions": (),
            },
        ),
        migrations.CreateModel(
            name="Setting",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "use_doctrines_from_fittings_module",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Whether to use the doctrines from the Fittings modules in the doctrine dropdown. Note: The fittings module needs to be installed for this.",
                        verbose_name="Use Doctrines from Fittings module",
                    ),
                ),
            ],
            options={
                "verbose_name": "Setting",
                "verbose_name_plural": "Settings",
                "default_permissions": (),
            },
        ),
        migrations.AddField(
            model_name="fatlink",
            name="doctrine",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The FAT link doctrine",
                max_length=254,
            ),
        ),
    ]