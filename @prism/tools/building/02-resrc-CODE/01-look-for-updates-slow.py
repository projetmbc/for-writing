#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

if not YAML_CONFIGS[TAG_WORKFLOW]['ASK_GITHUB']:
    logging.warning("'NO SEARCH' for needed updates")
    exit(0)

import os
import re
import requests
import time

from bs4 import BeautifulSoup


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


EXT_SRC_DIR = PROJ_DIR / TAG_RESOURCES
EXT_SRC_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


REPORT_DIR = THIS_DIR.parent / "UPDATES"
REPORT_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


UPDATES_BACKUP_JSON = REPORT_DIR / "BACKUP.json"

if UPDATES_BACKUP_JSON.is_file():
    with UPDATES_BACKUP_JSON.open(mode = "r") as f:
        UPDATES_BACKUP = json_load(f)

else:
    UPDATES_BACKUP = dict()


UPDATES_NEEDED_JSON = REPORT_DIR / "NEEDED.json"


# ----------- #
# -- TOOLS -- #
# ----------- #

def get_github_default_branch(ids):
    url = f"https://api.github.com/repos/{ids}"

    try:
        response = requests.get(
            url,
            headers = GITHUB_HEADERS
        )

        if response.status_code == 403:
            logging.warning(
                f"Rate limit exceeded for {ids}, "
                f"trying 'main'"
            )

            return 'main'

        response.raise_for_status()

        data = response.json()

        return data.get('default_branch', 'main')

    except requests.exceptions.RequestException as e:
        logging.warning(
            f"Could not get default branch for {ids}, "
            f"trying 'main': {e}"
        )

        return 'main'


def get_github_last_date(ids):
    default_branch = get_github_default_branch(ids)

    url = (
        f"https://api.github.com/repos/{ids}/"
        f"commits/{default_branch}"
    )

    try:
        response = requests.get(
            url,
            headers = GITHUB_HEADERS
        )

        if response.status_code == 403:
            logging.error(f"'{ids}' (GitHub) - Rate limit exceeded")

            return None

        response.raise_for_status()

        data = response.json()

        return data['commit']['committer']['date']

    except requests.exceptions.RequestException as e:
        logging.error(f"'{ids}' (GitHub) - Date cannot be recovered")

        return None


# ---------------------------- #
# -- GITHUB TOKEN IF NEEDED -- #
# ---------------------------- #

GITHUB_TOKEN   = os.environ.get('GITHUB_TOKEN', None)
GITHUB_HEADERS = {}

if GITHUB_TOKEN:
    GITHUB_HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'

    logging.info("GitHub token configured (authenticated requests)")

else:
    logging.warning(
        '''
No GitHub token. Rate limit: 60 requests/hour.
Set GITHUB_TOKEN environment variable for 5000 requests/hour
        '''.strip()
    )


# ------------------------------------- #
# -- NEEDED UPDATES - GITHUB COMMITS -- #
# ------------------------------------- #

logging.info("Looking for needed updates")

for name, ids in GITHUB_IDS.items():
    logging.info(f"Check '{name}' GitHub project")

    try:
        last_date = get_github_last_date(ids)

        stored_date, needed = UPDATES_BACKUP.get(name, ('', None))

        if last_date is None:
            UPDATES_BACKUP[name] = (None, None)

        elif stored_date < last_date:
            UPDATES_BACKUP[name] = (last_date, True)

        else:
            UPDATES_BACKUP[name] = (stored_date, False)

        # Pause pour éviter de surcharger l'API
        time.sleep(0.5)

    except Exception as e:
        log_raise_error(
            context   = "Looking for last commit date",
            desc      = "Date cannot be recovered",
            exception = Exception,
        )


# ----------------------------------------------- #
# -- NEEDED UPDATES - SCIENTIFIC COLOUR MAPS 8 -- #
# ----------------------------------------------- #

try:
    response = requests.get("https://www.fabiocrameri.ch/colourmaps")
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()

    pattern = r'Version\s+[\d.]+\s+\((\d{2})\.(\d{2})\.(\d{4})'
    match = re.search(pattern, text)

    if match:
        day   = match.group(1)
        month = match.group(2)
        year  = match.group(3)

        last_date = f"{year}-{month}-{day}T12:00:00Z"

        stored_date, needed = UPDATES_BACKUP.get(TAG_SCICOLMAPS, ('', None))

        if stored_date < last_date:
            UPDATES_BACKUP[TAG_SCICOLMAPS] = (last_date, True)

        else:
            UPDATES_BACKUP[TAG_SCICOLMAPS] = (stored_date, False)

    else:
        log_raise_error(
            context   = "Looking for last date",
            desc      = "'Scientific Colour Maps 8' date not found",
            exception = ValueError,
        )

except Exception as e:
    log_raise_error(
        context   = "Looking for last date",
        desc      = "'Scientific Colour Maps 8' date not found",
        exception = Exception,
    )


# -------------------- #
# -- UPDATES NEEDED -- #
# -------------------- #

needed_updates = {
    n: s
    for n, (d, s) in UPDATES_BACKUP.items()
}

if None in needed_updates.values():
    which_src = []

    for name in needed_updates:
        if needed_updates[name] is None:
            which_src.append(name)

    plurial = "" if len(which_src) == 1 else "s"

    which_src.sort(key = lambda n: n.lower())
    which_src = '\n'.join([
        f"    + {n}"
        for n in which_src
    ])

    which_src = f"See:\n{which_src}"

    start_desc = "Some dates" if plurial else "One date"

    log_raise_error(
        context   = "Extra source updates",
        desc      = f"{start_desc} uncovered.",
        exception = Exception,
        xtra      = which_src
    )


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

logging.info(f"Update '{UPDATES_BACKUP_JSON.name}' file")

UPDATES_BACKUP_JSON.write_text(
    json_dumps(UPDATES_BACKUP)
)


logging.info(f"Update '{UPDATES_NEEDED_JSON.name}' file")

UPDATES_NEEDED_JSON.write_text(
    json_dumps(needed_updates)
)
