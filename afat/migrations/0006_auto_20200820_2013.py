# Generated by Django 2.2.14 on 2020-08-20 20:13

# Django
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("afat", "0005_auto_20200816_2042"),
    ]

    operations = [
        migrations.CreateModel(
            name="AFatLinkType",
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
                ("name", models.CharField(max_length=254)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="afatlink",
            name="link_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="afat.AFatLinkType",
            ),
        ),
    ]
