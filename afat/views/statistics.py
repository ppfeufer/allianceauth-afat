"""
Statistics related views
"""

# Standard Library
import calendar
from collections import OrderedDict
from datetime import datetime

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required
from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# Alliance Auth AFAT
from afat import __title__
from afat.helper.views import (
    characters_with_permission,
    current_month_and_year,
    get_random_rgba_color,
    user_has_any_perms,
)
from afat.models import Fat
from afat.utils import get_or_create_alliance_info, get_or_create_corporation_info

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


@login_required()
@permission_required(perm="afat.basic_access")
def overview(request: WSGIRequest, year: int = None) -> HttpResponse:
    """
    Statistics main view

    :param request:
    :type request:
    :param year:
    :type year:
    :return:
    :rtype:
    """

    if year is None:
        year = datetime.now().year

    user_can_see_other_corps = False

    if user_has_any_perms(
        user=request.user,
        perm_list=["afat.stats_corporation_other", "afat.manage_afat"],
    ):
        user_can_see_other_corps = True
        basic_access_permission = Permission.objects.select_related("content_type").get(
            content_type__app_label="afat", codename="basic_access"
        )

        characters_with_access = characters_with_permission(
            permission=basic_access_permission
        )

        data = {"No Alliance": [1]}
        sanity_check = {}

        # Group corporations by alliance
        for character_with_access in characters_with_access:
            alliance_name = character_with_access.alliance_name or "No Alliance"
            corp_id = character_with_access.corporation_id
            corp_name = character_with_access.corporation_name

            if alliance_name not in data:
                data[alliance_name] = [character_with_access.alliance_id]

            if corp_id not in sanity_check:
                data[alliance_name].append((corp_id, corp_name))
                sanity_check[corp_id] = corp_id
    elif request.user.has_perm(perm="afat.stats_corporation_own"):
        data = [
            (
                request.user.profile.main_character.corporation_id,
                request.user.profile.main_character.corporation_name,
            )
        ]
    else:
        data = None

    months = _calculate_year_stats(request=request, year=year)

    context = {
        "data": data,
        "charstats": months,
        "year": year,
        "year_current": datetime.now().year,
        "year_prev": int(year) - 1,
        "year_next": int(year) + 1,
        "user_can_see_other_corps": user_can_see_other_corps,
    }

    logger.info(msg=f"Statistics overview called by {request.user}")

    return render(
        request=request,
        template_name="afat/view/statistics/statistics-overview.html",
        context=context,
    )


def _calculate_year_stats(request, year) -> dict:
    """
    Calculate statistics for the year

    :param request:
    :type request:
    :param year:
    :type year:
    :return:
    :rtype:
    """

    months = {"total": {}, "characters": []}

    # Get all characters for the user and order by userprofile and character name
    characters = EveCharacter.objects.filter(
        character_ownership__user=request.user
    ).order_by("-userprofile", "character_name")

    # Get all FATs for the year and group by character and month
    fats_in_year = (
        Fat.objects.filter(fatlink__created__year=year, character__in=characters)
        .values("character__character_id", "fatlink__created__month")
        .annotate(fat_count=Count("id"))
    )

    # Initialize character data
    character_data = {
        char.character_id: {"name": char.character_name, "fats": {}}
        for char in characters
    }

    # Populate the months and character data
    for result in fats_in_year:
        month = int(result["fatlink__created__month"])
        char_id = int(result["character__character_id"])
        fat_count = int(result["fat_count"])

        # Update total fats per month
        if month not in months["total"]:
            months["total"][month] = 0

        months["total"][month] += fat_count

        # Update character fats per month
        character_data[char_id]["fats"][month] = fat_count

    # Sort character fats by month and add to the result,
    # excluding characters with no FATs
    for char_id, data in character_data.items():
        if data["fats"]:  # Only include characters with FATs
            sorted_fats = dict(sorted(data["fats"].items()))
            months["characters"].append((data["name"], sorted_fats, char_id))

    return months


@login_required()
@permission_required(perm="afat.basic_access")
def character(  # pylint: disable=too-many-locals
    request: WSGIRequest, charid: int, year: int = None, month: int = None
) -> HttpResponse:
    """
    Character statistics view

    :param request:
    :type request:
    :param charid:
    :type charid:
    :param year:
    :type year:
    :param month:
    :type month:
    :return:
    :rtype:
    """

    current_month, current_year = current_month_and_year()
    eve_character = EveCharacter.objects.get(character_id=charid)
    valid = [
        char.character for char in CharacterOwnership.objects.filter(user=request.user)
    ]

    can_view_character = True

    # Check if the user can view another corporation's statistics or manage AFAT
    if eve_character not in valid and not user_has_any_perms(
        user=request.user,
        perm_list=[
            "afat.stats_corporation_other",
            "afat.manage_afat",
        ],
    ):
        can_view_character = False

    # Check if the user if by any chance in the same corporation as the character
    # and can view own corporation statistics
    if (
        eve_character not in valid
        and eve_character.corporation_id
        == request.user.profile.main_character.corporation_id
        and request.user.has_perm(perm="afat.stats_corporation_own")
    ):
        can_view_character = True

    # If the user cannot view the character's statistics, send him home …
    if can_view_character is False:
        messages.warning(
            request=request,
            message=mark_safe(
                s=gettext(
                    "<h4>Warning!</h4>"
                    "<p>You do not have permission to view "
                    "statistics for this character.</p>"
                )
            ),
        )

        return redirect(to="afat:dashboard")

    if not month or not year:
        messages.error(
            request=request,
            message=mark_safe(
                s=gettext("<h4>Warning!</h4><p>Date information not complete!</p>")
            ),
        )

        return redirect(to="afat:dashboard")

    fats = Fat.objects.filter(
        character__character_id=charid,
        fatlink__created__month=month,
        fatlink__created__year=year,
    )

    # Data for ship type pie chart
    data_ship_type = {}

    for fat in fats:
        if fat.shiptype in data_ship_type:
            continue

        data_ship_type[fat.shiptype] = fats.filter(shiptype=fat.shiptype).count()

    colors = []

    for _ in data_ship_type:
        bg_color_str = get_random_rgba_color()
        colors.append(bg_color_str)

    data_ship_type = [
        # Ship type can be None, so we need to convert to string here
        list(str(key) for key in data_ship_type),
        list(data_ship_type.values()),
        colors,
    ]

    # Data for by Time Line Chart
    data_time = {}

    for i in range(0, 24):
        data_time[i] = fats.filter(fatlink__created__hour=i).count()

    data_time = [
        list(data_time.keys()),
        list(data_time.values()),
        [get_random_rgba_color()],
    ]

    context = {
        "character": eve_character,
        "month": month,
        "month_current": current_month,
        "month_prev": int(month) - 1,
        "month_next": int(month) + 1,
        "month_with_year": f"{year}{month:02d}",
        "month_current_with_year": f"{current_year}{current_month:02d}",
        "month_next_with_year": f"{year}{int(month) + 1:02d}",
        "month_prev_with_year": f"{year}{int(month) - 1:02d}",
        "year": year,
        "year_current": current_year,
        "year_prev": int(year) - 1,
        "year_next": int(year) + 1,
        "data_ship_type": data_ship_type,
        "data_time": data_time,
        "fats": fats,
    }

    month_name = calendar.month_name[int(month)]
    logger.info(
        msg=(
            f"Character statistics for {eve_character} ({month_name} {year}) "
            f"called by {request.user}"
        )
    )

    return render(
        request=request,
        template_name="afat/view/statistics/statistics-character.html",
        context=context,
    )


@login_required()
@permissions_required(
    perm=(
        "afat.stats_corporation_other",
        "afat.stats_corporation_own",
        "afat.manage_afat",
    )
)
def corporation(  # pylint: disable=too-many-statements too-many-branches too-many-locals
    request: WSGIRequest, corpid: int = 0000, year: int = None, month: int = None
) -> HttpResponse:
    """
    Corp statistics view

    :param request:
    :type request:
    :param corpid:
    :type corpid:
    :param year:
    :type year:
    :param month:
    :type month:
    :return:
    :rtype:
    """

    if not year:
        year = datetime.now().year

    current_month, current_year = current_month_and_year()

    # Check character has permission to view other corp stats
    if int(request.user.profile.main_character.corporation_id) != int(corpid):
        if not user_has_any_perms(
            user=request.user,
            perm_list=["afat.stats_corporation_other", "afat.manage_afat"],
        ):
            messages.warning(
                request=request,
                message=mark_safe(
                    s=gettext(
                        "<h4>Warning!</h4>"
                        "<p>You do not have permission to view statistics "
                        "for that corporation.</p>"
                    )
                ),
            )

            return redirect(to="afat:dashboard")

    corp = get_or_create_corporation_info(corporation_id=corpid)
    corp_name = corp.corporation_name

    if not month:
        months = []

        for i in range(1, 13):
            corp_fats = Fat.objects.filter(
                character__corporation_id=corpid,
                fatlink__created__month=i,
                fatlink__created__year=year,
            ).count()

            avg_fats = 0
            if corp.member_count > 0:
                avg_fats = corp_fats / corp.member_count

            if corp_fats > 0:
                months.append((i, corp_fats, round(avg_fats, 2)))

        context = {
            "corporation": corp.corporation_name,
            "months": months,
            "corpid": corpid,
            "year": year,
            "year_current": current_year,
            "year_prev": int(year) - 1,
            "year_next": int(year) + 1,
            "type": 0,
        }

        return render(
            request=request,
            template_name="afat/view/statistics/statistics-corporation-year-overview.html",
            context=context,
        )

    fats = Fat.objects.filter(
        fatlink__created__month=month,
        fatlink__created__year=year,
        character__corporation_id=corpid,
    )

    characters = EveCharacter.objects.filter(corporation_id=corpid)

    # Data for Stacked Bar Graph
    # (label, color, [list of data for stack])
    data = {}

    for fat in fats:
        # if fat.shiptype in data.keys():
        if fat.shiptype in data:
            continue

        data[fat.shiptype] = {}

    chars = []

    for fat in fats:
        if fat.character.character_name in chars:
            continue

        chars.append(fat.character.character_name)

    for key, ship_type in data.items():
        for char in chars:
            ship_type[char] = 0

    for fat in fats:
        data[fat.shiptype][fat.character.character_name] += 1

    data_stacked = []

    for key, value in data.items():
        stack = []
        stack.append(key)
        stack.append(get_random_rgba_color())
        stack.append([])

        data_ = stack[2]

        for char in chars:
            data_.append(value[char])

        stack.append(data_)
        data_stacked.append(tuple(stack))

    data_stacked = [chars, data_stacked]

    # Data for By Time
    data_time = {}

    for i in range(0, 24):
        data_time[i] = fats.filter(fatlink__created__hour=i).count()

    data_time = [
        list(data_time.keys()),
        list(data_time.values()),
        [get_random_rgba_color()],
    ]

    # Data for By Weekday
    data_weekday = []

    for i in range(1, 8):
        data_weekday.append(fats.filter(fatlink__created__iso_week_day=i).count())

    data_weekday = [
        [
            gettext("Monday"),
            gettext("Tuesday"),
            gettext("Wednesday"),
            gettext("Thursday"),
            gettext("Friday"),
            gettext("Saturday"),
            gettext("Sunday"),
        ],
        data_weekday,
        [get_random_rgba_color()],
    ]

    chars = {}

    for char in characters:
        fat_c = fats.filter(character_id=char.id).count()
        chars[char.character_name] = (fat_c, char.character_id)

    context = {
        "corp": corp,
        "corporation": corp.corporation_name,
        "month": month,
        "month_current": datetime.now().month,
        "month_prev": int(month) - 1,
        "month_next": int(month) + 1,
        "month_with_year": f"{year}{month:02d}",
        "month_current_with_year": f"{current_year}{current_month:02d}",
        "month_next_with_year": f"{year}{int(month) + 1:02d}",
        "month_prev_with_year": f"{year}{int(month) - 1:02d}",
        "year": year,
        "year_current": datetime.now().year,
        "year_prev": int(year) - 1,
        "year_next": int(year) + 1,
        "data_stacked": data_stacked,
        "data_time": data_time,
        "data_weekday": data_weekday,
        "chars": chars,
    }

    month_name = calendar.month_name[int(month)]
    logger.info(
        msg=(
            f"Corporation statistics for {corp_name} ({month_name} {year}) "
            f"called by {request.user}"
        )
    )

    return render(
        request=request,
        template_name="afat/view/statistics/statistics-corporation.html",
        context=context,
    )


@login_required()
@permissions_required(perm=("afat.stats_corporation_other", "afat.manage_afat"))
def alliance(  # pylint: disable=too-many-statements too-many-branches too-many-locals
    request: WSGIRequest, allianceid: int, year: int = None, month: int = None
) -> HttpResponse:
    """
    Alliance statistics view

    :param request:
    :type request:
    :param allianceid:
    :type allianceid:
    :param year:
    :type year:
    :param month:
    :type month:
    :return:
    :rtype:
    """

    year = year or datetime.now().year

    ally = (
        get_or_create_alliance_info(alliance_id=allianceid)
        if allianceid != "000"
        else None
    )
    alliance_name = ally.alliance_name if ally else "No Alliance"

    current_month, current_year = current_month_and_year()

    if not month:
        months = []

        ally_fats_by_month = (
            Fat.objects.filter(
                character__alliance_id=allianceid,
                fatlink__created__year=year,
            )
            .values("fatlink__created__month")
            .annotate(fat_count=Count("id"))
        )

        for entry in ally_fats_by_month:
            months.append((entry["fatlink__created__month"], entry["fat_count"]))

        context = {
            "alliance": alliance_name,
            "months": months,
            "allianceid": allianceid,
            "year": year,
            "year_current": current_year,
            "year_prev": int(year) - 1,
            "year_next": int(year) + 1,
            "type": 1,
        }

        # /fleet-activity-tracking/statistics/alliance/<alliance_id>/<year>/
        return render(
            request=request,
            template_name="afat/view/statistics/statistics-alliance-year-overview.html",
            context=context,
        )

    if not month or not year:
        messages.error(
            request=request,
            message=mark_safe(
                s=gettext("<h4>Error!</h4><p>Date information incomplete.</p>")
            ),
        )

        return redirect(to="afat:dashboard")

    fats = Fat.objects.filter(
        character__alliance_id=allianceid,
        fatlink__created__month=month,
        fatlink__created__year=year,
    )

    # Data for ship type pie chart
    data_ship_type = fats.values("shiptype").annotate(count=Count("shiptype"))
    colors = [get_random_rgba_color() for _ in data_ship_type]

    data_ship_type = [
        list(str(item["shiptype"]) for item in data_ship_type),
        list(item["count"] for item in data_ship_type),
        colors,
    ]

    # Fats by corp and ship type
    data = {}
    corps_in_fats = set()

    for fat in fats:
        shiptype = fat.shiptype
        corp_name = fat.character.corporation_name

        if shiptype not in data:
            data[shiptype] = {}

        if corp_name not in data[shiptype]:
            data[shiptype][corp_name] = 0

        data[shiptype][corp_name] += 1
        corps_in_fats.add(corp_name)

    corps_in_fats = list(corps_in_fats)

    if None in data:
        data["Unknown"] = data.pop(None)

    data_stacked = [
        (key, get_random_rgba_color(), [value.get(corp, 0) for corp in corps_in_fats])
        for key, value in data.items()
    ]

    data_stacked = [corps_in_fats, data_stacked]

    corporations_in_alliance = EveCorporationInfo.objects.filter(alliance=ally)

    # Avg fats by corp
    data_avgs = {
        corp.corporation_name: round(
            fats.filter(character__corporation_id=corp.corporation_id).count()
            / corp.member_count,
            2,
        )
        for corp in corporations_in_alliance
    }

    data_avgs = OrderedDict(sorted(data_avgs.items(), key=lambda x: x[1], reverse=True))
    data_avgs = [
        list(data_avgs.keys()),
        list(data_avgs.values()),
        get_random_rgba_color(),
    ]

    # Fats by Time
    data_time = {i: fats.filter(fatlink__created__hour=i).count() for i in range(24)}

    data_time = [
        list(data_time.keys()),
        list(data_time.values()),
        [get_random_rgba_color()],
    ]

    # Fats by weekday
    data_weekday = [
        [
            gettext("Monday"),
            gettext("Tuesday"),
            gettext("Wednesday"),
            gettext("Thursday"),
            gettext("Friday"),
            gettext("Saturday"),
            gettext("Sunday"),
        ],
        [fats.filter(fatlink__created__iso_week_day=i).count() for i in range(1, 8)],
        [get_random_rgba_color()],
    ]

    # Corp list
    corps = {}

    for corp in corporations_in_alliance:
        c_fats = fats.filter(character__corporation_id=corp.corporation_id).count()
        avg = c_fats / corp.member_count
        corps[corp] = (corp.corporation_id, c_fats, round(avg, 2))

    corps = OrderedDict(sorted(corps.items(), key=lambda x: x[1][2], reverse=True))

    context = {
        "alliance": alliance_name,
        "ally": ally,
        "month": month,
        "month_current": current_month,
        "month_prev": int(month) - 1,
        "month_next": int(month) + 1,
        "month_with_year": f"{year}{month:02d}",
        "month_current_with_year": f"{current_year}{current_month:02d}",
        "month_next_with_year": f"{year}{int(month) + 1:02d}",
        "month_prev_with_year": f"{year}{int(month) - 1:02d}",
        "year": year,
        "year_current": current_year,
        "year_prev": int(year) - 1,
        "year_next": int(year) + 1,
        "data_stacked": data_stacked,
        "data_avgs": data_avgs,
        "data_time": data_time,
        "data_weekday": data_weekday,
        "corps": corps,
        "data_ship_type": data_ship_type,
    }

    month_name = calendar.month_name[int(month)]
    logger.info(
        msg=(
            f"Alliance statistics for {alliance_name} ({month_name} {year}) "
            f"called by {request.user}"
        )
    )

    return render(
        request=request,
        template_name="afat/view/statistics/statistics-alliance.html",
        context=context,
    )
