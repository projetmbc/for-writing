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


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

SQL_GET_PAL = "SELECT source, name, kind FROM hash WHERE name = ? AND is_kept = 1"


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR
while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR      = PROJ_DIR / 'tools' / 'building' / 'AUDIT'
HUMAN_KIND_YAML = AUDIT_DIR / "HUMAN-KIND.yaml"
SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"

PENDING_REKINDS = dict()

# ----------------- #
# -- FUNCTIONS   -- #
# ----------------- #

def fetch_palette(name):
    with sqlite3.connect(SQLITE_DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(SQL_GET_PAL, (name,))
        return cursor.fetchone()

def apply_rename():
    global PENDING_REKINDS

    with HUMAN_KIND_YAML.open('r') as f:
        last_kinds = safe_load(f)

    for name, (source, kinds) in PENDING_REKINDS.items():
        if not source in last_kinds:
            last_kinds[source] = dict()

        last_kinds[source][name] = kinds

    HUMAN_KIND_YAML.write_text(
        yaml_dump(last_kinds)
    )

def show_pending():
    global PENDING_REKINDS

    if not PENDING_REKINDS:
        print("[yellow]Aucun renommage en attente.[/yellow]")
        return

    table = Table(title="Renommages à valider")
    table.add_column("Ancien Nom", style="red")
    table.add_column("Alias Proposé", style="green")

    for name, (source, kinds) in PENDING_REKINDS.items():
        table.add_row(
            f"{name} [{source}]",
            kinds
        )

    print(table)

    if Confirm.ask("Voulez-vous valider TOUS ces changements en base de données ?"):
        apply_rename()

        PENDING_REKINDS = dict()

        print("[bold green]Données persistantes mises à jour ![/bold green]")

# ----------------- #
# -- MAIN LOOP   -- #
# ----------------- #

def run_app():
    print(Panel.fit("[bold blue]Gestionnaire de Palettes & Alias[/bold blue]",
                    subtitle="Commands: 'rev' pour réviser, 'q' pour quitter"))

    while True:
        query = Prompt.ask("\n[bold cyan]Type de la palette (ou commande)[/bold cyan]")

        if query.lower() in ['quit']:
            break

        # Mode révision
        if query.lower() == 'save':
            show_pending()
            continue

        # Recherche de la palette
        res = fetch_palette(query)

        if res:
            source, name, kind = res

            print(f"[bold]Source found:[/bold] [italic]{source}[/italic]")

            print(f"[bold]Type found:[/bold] [italic]{kind}[/italic]")

            # Option de renommage
            kind = Prompt.ask(f"Entrez le type pour '{name}' (laisser vide pour ignorer)", default="")

            if kind and kind != name:
                PENDING_REKINDS[name] = (source, kind)

                print(f"[yellow]✔ Type '{kind}' sauvegardé en mémoire.[/yellow]")
        else:
            print(f"[red]Palette '{query}' introuvable.[/red]")

if __name__ == "__main__":
    if not SQLITE_DB_FILE.exists():
        print(f"[bold red]Erreur: DB introuvable à {SQLITE_DB_FILE}[/bold red]")
    else:
        run_app()
