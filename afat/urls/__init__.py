"""
URLs for the AFAT app
"""

# Django
from django.urls import include, path

# Alliance Auth AFAT
from afat.constants import INTERNAL_URL_PREFIX
from afat.urls.ajax import urls as ajax_urls
from afat.urls.dashboard import urls as dashboard_urls
from afat.urls.fatlinks import urls as fatlinks_urls
from afat.urls.logs import urls as logs_urls
from afat.urls.statistics import urls as statistics_urls

app_name: str = "afat"

urlpatterns = [
    # Dashboard
    path(route="", view=include(dashboard_urls)),
    # Log urls
    path(route="logs/", view=include(logs_urls)),
    # FAT Links urls
    path(route="fatlinks/", view=include(fatlinks_urls)),
    # Statistics urls
    path(route="statistics/", view=include(statistics_urls)),
    # Ajax calls urls
    path(route=f"{INTERNAL_URL_PREFIX}/ajax/", view=include(ajax_urls)),
]
