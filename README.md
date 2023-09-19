# Alliance Auth AFAT — Another Fleet Activity Tracker<a name="alliance-auth-afat-%E2%80%94-another-fleet-activity-tracker"></a>

[![Version](https://img.shields.io/pypi/v/allianceauth-afat?label=release)](https://pypi.org/project/allianceauth-afat/)
[![License](https://img.shields.io/badge/license-GPLv3-green)](https://pypi.org/project/allianceauth-afat/)
[![Python](https://img.shields.io/pypi/pyversions/allianceauth-afat)](https://pypi.org/project/allianceauth-afat/)
[![Django](https://img.shields.io/pypi/djversions/allianceauth-afat?label=django)](https://pypi.org/project/allianceauth-afat/)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](http://black.readthedocs.io/en/latest/)
[![Automated Checks](https://github.com/ppfeufer/allianceauth-afat/actions/workflows/automated-checks.yml/badge.svg)](https://github.com/ppfeufer/allianceauth-afat/actions/workflows/automated-checks.yml)
[![codecov](https://codecov.io/gh/ppfeufer/allianceauth-afat/branch/master/graph/badge.svg?token=GNE88NUAKK)](https://codecov.io/gh/ppfeufer/allianceauth-afat)
[![Translation status](https://weblate.ppfeufer.de/widget/alliance-auth-apps/allianceauth-afat/svg-badge.svg)](https://weblate.ppfeufer.de/engage/alliance-auth-apps/)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](https://github.com/ppfeufer/aa-forum/blob/master/CODE_OF_CONDUCT.md)
[![Discord](https://img.shields.io/discord/790364535294132234?label=discord)](https://discord.gg/zmh52wnfvM)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/N4N8CL1BY)

An Improved FAT/PAP System for
[Alliance Auth](https://gitlab.com/allianceauth/allianceauth).

______________________________________________________________________

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=1 -->

- [Alliance Auth AFAT — Another Fleet Activity Tracker](#alliance-auth-afat-%E2%80%94-another-fleet-activity-tracker)
  - [Features and Highlights](#features-and-highlights)
  - [Screenshots](#screenshots)
    - [Dashboard](#dashboard)
    - [Fat Link List](#fat-link-list)
    - [Fat Link Details](#fat-link-details)
    - [Add Fat Link View for FCs](#add-fat-link-view-for-fcs)
  - [Installation](#installation)
    - [Important](#important)
    - [Step 1: Install the App](#step-1-install-the-app)
    - [Step 2: Update Your AA Settings](#step-2-update-your-aa-settings)
    - [Step 3: Finalizing the Installation](#step-3-finalizing-the-installation)
  - [Updating](#updating)
  - [Data Migration](#data-migration)
    - [Import From Native FAT](#import-from-native-fat)
    - [Import From ImicusFAT](#import-from-imicusfat)
      - [Uninstall ImicusFAT](#uninstall-imicusfat)
  - [Settings](#settings)
  - [Permissions](#permissions)
  - [Changelog](#changelog)
  - [Translation Status](#translation-status)
  - [Contributing](#contributing)
  - [Credits](#credits)

<!-- mdformat-toc end -->

______________________________________________________________________

## Features and Highlights<a name="features-and-highlights"></a>

- Automatic tracking of participation on FAT links created via ESI
- Multiple ESI fleets (with your alts)
- Manually end ESI tracking per fleet
- Fleet type classification (can be added in the admin backend)
- Ship type overview per FAT link
- Graphical statistics views
- Custom module name
- Re-open FAT link if the FAT link has expired and is within the defined grace time
  (only for clickable FAT links)
- Manually add pilots to clickable FAT links, in case they missed clicking the link
  (for a period of 24 hours after the FAT links original expiry time)
- Log for the following actions (Logs are kept for a certain time, 60 days per default):
  - Create FAT link
  - Change FAT link
  - Remove FAT link
  - Re-open FAT link
  - Manually add pilot to FAT link
  - Remove pilot from FAT link

AFAT will work alongside the built-in native FAT System and ImicusFAT.
However, data doesn't share, but you can migrate their data to AFAT, for more
information, see below.

## Screenshots<a name="screenshots"></a>

### Dashboard<a name="dashboard"></a>

![Dashboard](https://raw.githubusercontent.com/ppfeufer/allianceauth-afat/master/docs/images/afat-dashboard.png "Dashboard")

### Fat Link List<a name="fat-link-list"></a>

![Fat Link List](https://raw.githubusercontent.com/ppfeufer/allianceauth-afat/master/docs/images/fatlink-list.png "Fat Link List")

### Fat Link Details<a name="fat-link-details"></a>

![Fat Link Details](https://raw.githubusercontent.com/ppfeufer/allianceauth-afat/master/docs/images/ship-type-overview.png "Fat Link Details")

### Add Fat Link View for FCs<a name="add-fat-link-view-for-fcs"></a>

![Add Fat Link View for FCs](https://raw.githubusercontent.com/ppfeufer/allianceauth-afat/master/docs/images/add-fatlink.png "Add Fat Link View for FCs")

## Installation<a name="installation"></a>

### Important<a name="important"></a>

This app is a plugin for Alliance Auth. If you don't have Alliance Auth running already,
please install it first before proceeding. (See the official
[AA installation guide](https://allianceauth.readthedocs.io/en/latest/installation/allianceauth.html)
for details)

**For users migrating from one of the other FAT systems, please read the specific
instructions FIRST.**

### Step 1: Install the App<a name="step-1-install-the-app"></a>

Make sure you're in the virtual environment (venv) of your Alliance Auth installation.
Then install the latest version:

```bash
pip install allianceauth-afat
```

### Step 2: Update Your AA Settings<a name="step-2-update-your-aa-settings"></a>

Configure your AA settings in your `local.py` as follows:

- Add `'afat',` to `INSTALLED_APPS`
- Add the scheduled tasks

```python
# AFAT - https://github.com/ppfeufer/allianceauth-afat
CELERYBEAT_SCHEDULE["afat_update_esi_fatlinks"] = {
    "task": "afat.tasks.update_esi_fatlinks",
    "schedule": crontab(minute="*/1"),
}

CELERYBEAT_SCHEDULE["afat_logrotate"] = {
    "task": "afat.tasks.logrotate",
    "schedule": crontab(minute="0", hour="1"),
}
```

### Step 3: Finalizing the Installation<a name="step-3-finalizing-the-installation"></a>

Run migrations & copy static files

```bash
python manage.py collectstatic
python manage.py migrate
```

Restart your supervisor services for AA.

## Updating<a name="updating"></a>

To update your existing installation of AFAT, first enable your
virtual environment (venv) of your Alliance Auth installation.

```bash
pip install -U allianceauth-afat

python manage.py collectstatic
python manage.py migrate
```

Finally, restart your supervisor services for AA

It is possible that some versions need some more changes. Always read the
[release notes](https://github.com/ppfeufer/allianceauth-afat/releases) to find out
more.

## Data Migration<a name="data-migration"></a>

Right after the **initial** installation and running migrations,
you can import the data from Alliance Auth's native FAT system or from ImicusFAT if
you have used one of these until now.

### Import From Native FAT<a name="import-from-native-fat"></a>

To import from the native FAT module, simply run the following command:

```shell
python myauth/manage.py afat_import_from_allianceauth_fat
```

### Import From ImicusFAT<a name="import-from-imicusfat"></a>

To import from the ImicusFAT module, simply run the following command:

```shell
python myauth/manage.py afat_import_from_imicusfat
```

#### Uninstall ImicusFAT<a name="uninstall-imicusfat"></a>

Now that you've migrated, you can uninstal `ImicusFAT`.

First, remove all Django migrations for `ImicusFAT` with:

```shell
python manage.py migrate imicusfat zero
```

This will remove all migrations for `ImicusFAT` including its DB tables.

Should this command throw an error, a bit of manual labor is needed, but nothing you
can't handle, I'm sure.

```shell
python manage.py migrate imicusfat zero --fake
```

And remove all DB tables beginning with `imicusfat_` from your DB manually afterwards.

Now that the DB is cleaned up, time to remove te app.

```shell
pip uninstall allianceauth-imicusfat
```

Now remove `imicusfat` from your `INSTALLED_APPS` in your `local.py`, restart
supervisor and ... Done!

## Settings<a name="settings"></a>

To customize the module, the following settings are available.

| Name                                   | Description                                                      | Default Value           | Value Type |
| :------------------------------------- | :--------------------------------------------------------------- | :---------------------- | :--------- |
| AFAT_APP_NAME                          | Custom application name, in case you'd like a different name     | Fleet Activity Tracking | string     |
| AFAT_DEFAULT_FATLINK_EXPIRY_TIME       | Default expiry time for clickable FAT links in Minutes           | 60                      | int        |
| AFAT_DEFAULT_FATLINK_REOPEN_GRACE_TIME | Time in minutes a FAT link can be re-opened after it has expired | 60                      | int        |
| AFAT_DEFAULT_FATLINK_REOPEN_DURATION   | Time in minutes a FAT link is re-opened                          | 60                      | int        |
| AFAT_DEFAULT_LOG_DURATION              | Time in days before log entries are being removed from the DB    | 60                      | int        |

## Permissions<a name="permissions"></a>

| Name                    | Description                              | Notes                                                                                                                                                                           |
| :---------------------- | :--------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| basic_access            | Can access the AFAT module               | Your line member probably want this permission, so they can see the module and click the FAT links they are given. They also can see their own statistics with this permission. |
| manage_afat             | Can manage the AFAT module               | Your Military lead probably should get this permission                                                                                                                          |
| add_fatlink             | Can create FAT Links                     | Your regular FC or who ever should be able to add FAT links should have this permission                                                                                         |
| stats_corporation_own   | Can see own corporation statistics       |                                                                                                                                                                                 |
| stats_corporation_other | Can see statistics of other corporations |                                                                                                                                                                                 |
| logs_view               | Can view the modules logs                |                                                                                                                                                                                 |

## Changelog<a name="changelog"></a>

To keep track of all changes, please read the
[Changelog](https://github.com/ppfeufer/allianceauth-afat/blob/master/CHANGELOG.md).

## Translation Status<a name="translation-status"></a>

[![Translation status](https://weblate.ppfeufer.de/widget/alliance-auth-apps/allianceauth-afat/multi-auto.svg)](https://weblate.ppfeufer.de/engage/alliance-auth-apps/)

Do you want to help translate this app into your language or improve the existing
translation? - [Join our team of translators][weblate engage]!

## Contributing<a name="contributing"></a>

You want to contribute to this project? That's cool!

Please make sure to read the [contribution guidelines](https://github.com/ppfeufer/allianceauth-afat/blob/master/CONTRIBUTING.md).\
(I promise, it's not much, just some basics)

## Credits<a name="credits"></a>

AFAT is maintained by @ppfeufer and is based on
[ImicusFAT](https://gitlab.com/evictus.iou/allianceauth-imicusfat)
by @exiom with @Aproia and @ppfeufer which is based on
[allianceauth-bfat](https://gitlab.com/colcrunch/allianceauth-bfat) by @colcrunch

Both of these modules are no longer maintained and are deprecated. Both modules will
not run with the latest stable releases of Alliance Auth.

<!-- Inline Links -->

[weblate engage]: https://weblate.ppfeufer.de/engage/alliance-auth-apps/ "Weblate Translations"
