"""
URL configuration
"""

# Django
from django.urls import path

# Alliance Auth AFAT
from afat.views import dashboard, fatlinks, logs, statistics

app_name: str = "afat"

urlpatterns = [
    # Dashboard
    path("", dashboard.overview, name="dashboard"),
    # Stats main page
    path("statistics/", statistics.overview, name="statistics_overview"),
    path("statistics/(<int:year>/", statistics.overview, name="statistics_overview"),
    # Stats corp
    path(
        "statistics/corporation/",
        statistics.corporation,
        name="statistics_corporation",
    ),
    path(
        "statistics/corporation/<int:corpid>/",
        statistics.corporation,
        name="statistics_corporation",
    ),
    path(
        "statistics/corporation/<int:corpid>/<int:year>/",
        statistics.corporation,
        name="statistics_corporation",
    ),
    path(
        "statistics/corporation/<int:corpid>/<int:year>/<int:month>/",
        statistics.corporation,
        name="statistics_corporation",
    ),
    # Stats char
    path("statistics/character/", statistics.character, name="statistics_character"),
    path(
        "statistics/character/<int:charid>/",
        statistics.character,
        name="statistics_character",
    ),
    path(
        "statistics/character/<int:charid>/<int:year>/<int:month>/",
        statistics.character,
        name="statistics_character",
    ),
    # Stats alliance
    path("statistics/alliance/", statistics.alliance, name="statistics_alliance"),
    path(
        "statistics/alliance/<int:allianceid>/",
        statistics.alliance,
        name="statistics_alliance",
    ),
    path(
        "statistics/alliance/<int:allianceid>/<int:year>/",
        statistics.alliance,
        name="statistics_alliance",
    ),
    path(
        "statistics/alliance/<int:allianceid>/<int:year>/<int:month>/",
        statistics.alliance,
        name="statistics_alliance",
    ),
    # Fat links list actions
    path("fatlinks/", fatlinks.overview, name="fatlinks_overview"),
    path("fatlinks/<int:year>/", fatlinks.overview, name="fatlinks_overview"),
    # Fat link actions
    path("fatlink/add/", fatlinks.add_fatlink, name="fatlinks_add_fatlink"),
    path(
        "fatlinks/link/create/esi-fatlink/",
        fatlinks.create_esi_fatlink,
        name="fatlinks_create_esi_fatlink",
    ),
    path(
        "fatlink/create/esi-fatlink/callback/<str:fatlink_hash>/",
        fatlinks.create_esi_fatlink_callback,
        name="fatlinks_create_esi_fatlink_callback",
    ),
    path(
        "fatlink/create/clickable-fatlink/",
        fatlinks.create_clickable_fatlink,
        name="fatlinks_create_clickable_fatlink",
    ),
    path(
        "fatlink/<str:fatlink_hash>/details/",
        fatlinks.details_fatlink,
        name="fatlinks_details_fatlink",
    ),
    path(
        "fatlink/<str:fatlink_hash>/delete/",
        fatlinks.delete_fatlink,
        name="fatlinks_delete_fatlink",
    ),
    path(
        "fatlink/<str:fatlink_hash>/stop-esi-tracking/",
        fatlinks.close_esi_fatlink,
        name="fatlinks_close_esi_fatlink",
    ),
    path(
        "fatlink/<str:fatlink_hash>/re-open/",
        fatlinks.reopen_fatlink,
        name="fatlinks_reopen_fatlink",
    ),
    # Fat actions
    path(
        "fatlink/<str:fatlink_hash>/register/",
        fatlinks.add_fat,
        name="fatlinks_add_fat",
    ),
    path(
        "fatlink/<str:fatlink_hash>/fat/<int:fat_id>/delete/",
        fatlinks.delete_fat,
        name="fatlinks_delete_fat",
    ),
    # Log actions
    path("logs/", logs.overview, name="logs_overview"),
    # Ajax calls :: Dashboard
    path(
        "ajax/dashboard/fatlinks/recent/",
        dashboard.ajax_get_recent_fatlinks,
        name="dashboard_ajax_get_recent_fatlinks",
    ),
    path(
        "ajax/dashboard/fats/recent/character/<int:charid>/",
        dashboard.ajax_recent_get_fats_by_character,
        name="dashboard_ajax_get_recent_fats_by_character",
    ),
    # Ajax calls :: Fat links
    path(
        "ajax/fatlinks/fatlinks/year/<int:year>/",
        fatlinks.ajax_get_fatlinks_by_year,
        name="fatlinks_ajax_get_fatlinks_by_year",
    ),
    path(
        "ajax/fatlinks/fatlink/<str:fatlink_hash>/fats/",
        fatlinks.ajax_get_fats_by_fatlink,
        name="fatlinks_ajax_get_fats_by_fatlink",
    ),
    # Ajax calls :: Logs
    path("ajax/logs/", logs.ajax_get_logs, name="logs_ajax_get_logs"),
]
