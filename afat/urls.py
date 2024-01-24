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
    path(route="", view=dashboard.overview, name="dashboard"),
    # Stats main page
    path(route="statistics/", view=statistics.overview, name="statistics_overview"),
    path("statistics/<int:year>/", statistics.overview, name="statistics_overview"),
    # Stats corp
    path(
        route="statistics/corporation/",
        view=statistics.corporation,
        name="statistics_corporation",
    ),
    path(
        route="statistics/corporation/<int:corpid>/",
        view=statistics.corporation,
        name="statistics_corporation",
    ),
    path(
        route="statistics/corporation/<int:corpid>/<int:year>/",
        view=statistics.corporation,
        name="statistics_corporation",
    ),
    path(
        route="statistics/corporation/<int:corpid>/<int:year>/<int:month>/",
        view=statistics.corporation,
        name="statistics_corporation",
    ),
    # Stats char
    path(
        route="statistics/character/",
        view=statistics.character,
        name="statistics_character",
    ),
    path(
        route="statistics/character/<int:charid>/",
        view=statistics.character,
        name="statistics_character",
    ),
    path(
        route="statistics/character/<int:charid>/<int:year>/<int:month>/",
        view=statistics.character,
        name="statistics_character",
    ),
    # Stats alliance
    path(
        route="statistics/alliance/",
        view=statistics.alliance,
        name="statistics_alliance",
    ),
    path(
        route="statistics/alliance/<int:allianceid>/",
        view=statistics.alliance,
        name="statistics_alliance",
    ),
    path(
        route="statistics/alliance/<int:allianceid>/<int:year>/",
        view=statistics.alliance,
        name="statistics_alliance",
    ),
    path(
        route="statistics/alliance/<int:allianceid>/<int:year>/<int:month>/",
        view=statistics.alliance,
        name="statistics_alliance",
    ),
    # Fat links list actions
    path(route="fatlinks/", view=fatlinks.overview, name="fatlinks_overview"),
    path(
        route="fatlinks/<int:year>/", view=fatlinks.overview, name="fatlinks_overview"
    ),
    # Fat link actions
    path(route="fatlink/add/", view=fatlinks.add_fatlink, name="fatlinks_add_fatlink"),
    path(
        route="fatlinks/link/create/esi-fatlink/",
        view=fatlinks.create_esi_fatlink,
        name="fatlinks_create_esi_fatlink",
    ),
    path(
        route="fatlink/create/esi-fatlink/callback/<str:fatlink_hash>/",
        view=fatlinks.create_esi_fatlink_callback,
        name="fatlinks_create_esi_fatlink_callback",
    ),
    path(
        route="fatlink/create/clickable-fatlink/",
        view=fatlinks.create_clickable_fatlink,
        name="fatlinks_create_clickable_fatlink",
    ),
    path(
        route="fatlink/<str:fatlink_hash>/details/",
        view=fatlinks.details_fatlink,
        name="fatlinks_details_fatlink",
    ),
    path(
        route="fatlink/<str:fatlink_hash>/delete/",
        view=fatlinks.delete_fatlink,
        name="fatlinks_delete_fatlink",
    ),
    path(
        route="fatlink/<str:fatlink_hash>/stop-esi-tracking/",
        view=fatlinks.close_esi_fatlink,
        name="fatlinks_close_esi_fatlink",
    ),
    path(
        route="fatlink/<str:fatlink_hash>/re-open/",
        view=fatlinks.reopen_fatlink,
        name="fatlinks_reopen_fatlink",
    ),
    # Fat actions
    path(
        route="fatlink/<str:fatlink_hash>/register/",
        view=fatlinks.add_fat,
        name="fatlinks_add_fat",
    ),
    path(
        route="fatlink/<str:fatlink_hash>/fat/<int:fat_id>/delete/",
        view=fatlinks.delete_fat,
        name="fatlinks_delete_fat",
    ),
    # Log actions
    path(route="logs/", view=logs.overview, name="logs_overview"),
    # Ajax calls :: Dashboard
    path(
        route="ajax/dashboard/get-recent-fatlinks/",
        view=dashboard.ajax_get_recent_fatlinks,
        name="dashboard_ajax_get_recent_fatlinks",
    ),
    path(
        route="ajax/dashboard/get-recent-fats-by-character/<int:charid>/",
        view=dashboard.ajax_recent_get_fats_by_character,
        name="dashboard_ajax_get_recent_fats_by_character",
    ),
    # Ajax calls :: Fat links
    path(
        route="ajax/fatlinks/get-fatlinks-by-year/<int:year>/",
        view=fatlinks.ajax_get_fatlinks_by_year,
        name="fatlinks_ajax_get_fatlinks_by_year",
    ),
    path(
        route="ajax/fatlinks/get-fats-by-fatlink/<str:fatlink_hash>/",
        view=fatlinks.ajax_get_fats_by_fatlink,
        name="fatlinks_ajax_get_fats_by_fatlink",
    ),
    # Ajax calls :: Logs
    path(route="ajax/logs/", view=logs.ajax_get_logs, name="logs_ajax_get_logs"),
]
