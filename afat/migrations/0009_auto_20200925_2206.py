# Generated by Django 3.1.1 on 2020-09-25 22:06

# Django
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

# Alliance Auth AFAT
import afat.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("eveonline", "0012_index_additions"),
        ("afat", "0008_auto_20200912_1116"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="afatlinktype",
            options={
                "default_permissions": (),
                "verbose_name": "FAT Link Fleet Type",
                "verbose_name_plural": "FAT Link Fleet Types",
            },
        ),
        migrations.AddField(
            model_name="afatlink",
            name="is_esilink",
            field=models.BooleanField(
                default=False,
                help_text="Whether this fatlink was created via ESI or not",
            ),
        ),
        migrations.AddField(
            model_name="afatlinktype",
            name="is_enabled",
            field=models.BooleanField(
                db_index=True,
                default=True,
                help_text="Whether this fleettype is active or not",
            ),
        ),
        migrations.AlterField(
            model_name="afat",
            name="afatlink",
            field=models.ForeignKey(
                help_text="The fatlink the character registered at",
                on_delete=django.db.models.deletion.CASCADE,
                to="afat.afatlink",
            ),
        ),
        migrations.AlterField(
            model_name="afat",
            name="character",
            field=models.ForeignKey(
                help_text="Character who registered this fat",
                on_delete=django.db.models.deletion.CASCADE,
                to="eveonline.evecharacter",
            ),
        ),
        migrations.AlterField(
            model_name="afat",
            name="deleted_at",
            field=models.DateTimeField(
                blank=True, help_text="Has been deleted or not", null=True
            ),
        ),
        migrations.AlterField(
            model_name="afat",
            name="shiptype",
            field=models.CharField(
                help_text="The ship the character was flying", max_length=100, null=True
            ),
        ),
        migrations.AlterField(
            model_name="afat",
            name="system",
            field=models.CharField(
                help_text="The system the character is in", max_length=100, null=True
            ),
        ),
        migrations.AlterField(
            model_name="afatlink",
            name="afattime",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                help_text="When was this fatlink created",
            ),
        ),
        migrations.AlterField(
            model_name="afatlink",
            name="creator",
            field=models.ForeignKey(
                help_text="Who created the fatlink?",
                on_delete=models.SET(afat.models.get_sentinel_user),
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="afatlink",
            name="deleted_at",
            field=models.DateTimeField(
                blank=True, help_text="Has been deleted or not", null=True
            ),
        ),
        migrations.AlterField(
            model_name="afatlink",
            name="fleet",
            field=models.CharField(
                help_text="The fatlinks fleet name", max_length=254, null=True
            ),
        ),
        migrations.AlterField(
            model_name="afatlink",
            name="hash",
            field=models.CharField(help_text="The fatlinks hash", max_length=254),
        ),
        migrations.AlterField(
            model_name="afatlink",
            name="link_type",
            field=models.ForeignKey(
                help_text="The fatlinks fleet type, if it's set",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="afat.afatlinktype",
            ),
        ),
        migrations.AlterField(
            model_name="afatlinktype",
            name="deleted_at",
            field=models.DateTimeField(
                blank=True, help_text="Has this been deleted?", null=True
            ),
        ),
        migrations.AlterField(
            model_name="afatlinktype",
            name="name",
            field=models.CharField(
                help_text="Descriptive name of your fleet type", max_length=254
            ),
        ),
    ]
