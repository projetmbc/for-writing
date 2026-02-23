#!/usr/bin/env python3

from rich import print
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
import sys
import sqlite3
from pathlib import Path

# ----------------------------- #
# -- IMPORT LABUTILS - START -- #
THIS_DIR = Path(__file__).parent
LAB_DIR  = THIS_DIR.parent
sys.path.append(str(LAB_DIR))
from labutils import *

# -- IMPORT LABUTILS - END -- #

from yaml import (
    safe_load,
    dump as yaml_dump
)


ALL_CATEGOS_YAML = LAB_DIR.parent / 'config' / 'METADATA.yaml'

_ALL_CATEGOS = safe_load(ALL_CATEGOS_YAML.read_text())
_ALL_CATEGOS = _ALL_CATEGOS['CATEGORY']

ALL_CATEGOS = ', '.join(sorted(_ALL_CATEGOS))


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

SQL_GET_PAL = """
SELECT
    source, name, catego
FROM hash
WHERE name = ?
  AND is_kept = 1
"""


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR
while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR         = PROJ_DIR / 'tools' / 'building' / 'AUDIT'
HUMAN_CATEGO_YAML = AUDIT_DIR / "HUMAN-CATEGO.yaml"
SQLITE_DB_FILE    = AUDIT_DIR / "palettes.db"

PENDING_RECATEGOS = dict()


# ----------- #
# -- TOOLS -- #
# ----------- #

def fetch_palette(name):
    with sqlite3.connect(SQLITE_DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(SQL_GET_PAL, (name,))

        return cursor.fetchone()


def apply_rename():
    global PENDING_RECATEGOS

    with HUMAN_CATEGO_YAML.open('r') as f:
        last_CATEGOs = safe_load(f)

    for name, (source, categos) in PENDING_RECATEGOS.items():
        if not source in last_CATEGOs:
            last_CATEGOs[source] = dict()

        last_CATEGOs[source][name] = categos

    HUMAN_CATEGO_YAML.write_text(
        yaml_dump(last_CATEGOs)
    )


def show_pending():
    global PENDING_RECATEGOS

    if not PENDING_RECATEGOS:
        print("[yellow]No categos pending.[/yellow]")

        return

    table = Table(title = "Validate new categos")

    table.add_column("Old categos", style = "red")
    table.add_column("New categos", style = "green")

    for name, (source, categos) in PENDING_RECATEGOS.items():
        table.add_row(f"{name} [{source}]", categos)

    print(table)

    if Confirm.ask("Validate the changes?"):
        apply_rename()

        PENDING_RECATEGOS = dict()

        print("[bold green]Persistent data updated![/bold green]")


# --------------- #
# -- MAIN LOOP -- #
# --------------- #

def run_app():
    print(
        Panel.fit(
            "[bold blue]Pallet category manager[/bold blue]",
            subtitle = '(s)ave, (q)uit'
        )
    )

    while True:
        query = Prompt.ask(
            "\n[bold cyan]Palette categos (or command)[/bold cyan]"
        )

        if query.lower() in ['q', 'quit']:
            break

        # Mode révision
        if query.lower() in ['s', 'save']:
            show_pending()
            continue

        # Recherche de la palette
        res = fetch_palette(query)

        if res:
            source, name, catego = res

            print(
                 "[bold]Source:[/bold] "
                f"[italic]{source}[/italic]"
            )

            print(
                 "[bold]Categos:[/bold] "
                f"[italic]{catego}[/italic]"
            )

            print(
                 "[bold]Available categos:[/bold] "
                f"\n[italic]{ALL_CATEGOS}[/italic]"
            )

            # Option de renommage
            catego = Prompt.ask(
                f"Categos for '{name}' (type empty to ignore)",
                default = ''
            )

            if catego:
                PENDING_RECATEGOS[name] = (source, catego)

                print(
                    f"[yellow]✔ Categos '{catego}' "
                     "saved in memory.[/yellow]"
                )

        else:
            print(f"[red]No '{query}' palette found.[/red]")


if __name__ == "__main__":
    if not SQLITE_DB_FILE.exists():
        print(
             "[bold red]Missing file: "
            f"'{SQLITE_DB_FILE}'[/bold red]"
        )

    else:
        run_app()
