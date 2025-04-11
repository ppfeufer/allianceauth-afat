"""
Migration script to fix hstats affiliation in statistics.
"""

# Django
from django.core.management import BaseCommand

# Alliance Auth AFAT
from afat.models import Fat
from afat.providers import esi


def get_input(text) -> str:
    """
    Wrapped input to enable import

    :param text:
    :type text:
    :return:
    :rtype:
    """

    return input(text)


class Command(BaseCommand):
    """
    Fix affiliation in statistics
    """

    def _fix_affiliation_in_statistics(self) -> None:
        """
        Fix affiliation in statistics

        :return:
        :rtype:
        """

        all_fats = Fat.objects.all()
        # all_fats = Fat.objects.filter(pk=12)

        cache_character_corp_history = {}
        cache_corp_alliance_history = {}
        update_rows = []

        # Fix affiliation in statistics
        for fat in all_fats:
            corp_history = cache_character_corp_history.setdefault(
                fat.character.corporation_id,
                esi.client.Character.get_characters_character_id_corporationhistory(
                    character_id=fat.character.character_id
                ).results(),
            )

            for corp_entry in corp_history:
                if fat.fatlink.created <= corp_entry["start_date"]:
                    continue

                affiliation_corp_id = corp_entry["corporation_id"]
                alliance_history = cache_corp_alliance_history.setdefault(
                    affiliation_corp_id,
                    esi.client.Corporation.get_corporations_corporation_id_alliancehistory(
                        corporation_id=affiliation_corp_id
                    ).results(),
                )

                affiliation_alliance_id = next(
                    (
                        entry["alliance_id"]
                        for entry in alliance_history
                        if entry.get("alliance_id")
                        and fat.fatlink.created > entry["start_date"]
                    ),
                    None,
                )

                update_rows.append(
                    {
                        "fat_id": fat.pk,
                        "corporation_eve_id": affiliation_corp_id,
                        "alliance_eve_id": affiliation_alliance_id,
                    }
                )
                break

        # Update rows
        Fat.objects.bulk_update(
            objs=[
                Fat(
                    pk=row["fat_id"],
                    corporation_eve_id=row["corporation_eve_id"],
                    alliance_eve_id=row["alliance_eve_id"],
                )
                for row in update_rows
            ],
            fields=["corporation_eve_id", "alliance_eve_id"],
            batch_size=500,
        )

        self.stdout.write(msg=self.style.SUCCESS("Merge complete!"))

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        """
        Ask before running …

        :param args:
        :param options:
        :return:
        :rtype:
        """

        self.stdout.write(
            msg=self.style.SUCCESS(
                "This command will add the affiliation of pilots in all FATs so the "
                "statistics are correct. "
                "This might take quite a while depending on the number of pilots "
                "in your database. Please be patient."
            )
        )

        user_input = get_input(text="Are you sure you want to proceed? (yes/no) ")

        if user_input == "yes":
            self.stdout.write(msg="Starting migration. Please stand by.")
            self._fix_affiliation_in_statistics()
        else:
            self.stdout.write(msg=self.style.WARNING("Aborted."))
