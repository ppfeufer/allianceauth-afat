# Generated by Django 3.1.7 on 2021-03-30 12:26

# Django
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("afat", "0016_permissions_overhaul"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="afat",
            name="deleted_at",
        ),
        migrations.RemoveField(
            model_name="afatlink",
            name="deleted_at",
        ),
        migrations.RemoveField(
            model_name="afatlinktype",
            name="deleted_at",
        ),
        migrations.DeleteModel(
            name="AFatDelLog",
        ),
    ]
