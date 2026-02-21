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

SQL_GET_PAL = "SELECT source, name, catego FROM hash WHERE name = ? AND is_kept = 1"


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR
while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR      = PROJ_DIR / 'tools' / 'building' / 'AUDIT'
HUMAN_CATEGO_YAML = AUDIT_DIR / "HUMAN-CATEGO.yaml"
SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"

PENDING_REcategoS = dict()

# ----------------- #
# -- FUNCTIONS   -- #
# ----------------- #

def fetch_palette(name):
    with sqlite3.connect(SQLITE_DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(SQL_GET_PAL, (name,))
        return cursor.fetchone()

def apply_rename():
    global PENDING_REcategoS

    with HUMAN_CATEGO_YAML.open('r') as f:
        last_CATEGOs = safe_load(f)

    for name, (source, categos) in PENDING_REcategoS.items():
        if not source in last_CATEGOs:
            last_CATEGOs[source] = dict()

        last_CATEGOs[source][name] = categos

    HUMAN_CATEGO_YAML.write_text(
        yaml_dump(last_CATEGOs)
    )

def show_pending():
    global PENDING_REcategoS

    if not PENDING_REcategoS:
        print("[yellow]Aucun renommage en attente.[/yellow]")
        return

    table = Table(title="Renommages à valider")
    table.add_column("Ancien Nom", style="red")
    table.add_column("Alias Proposé", style="green")

    for name, (source, categos) in PENDING_REcategoS.items():
        table.add_row(
            f"{name} [{source}]",
            categos
        )

    print(table)

    if Confirm.ask("Voulez-vous valider TOUS ces changements en base de données ?"):
        apply_rename()

        PENDING_REcategoS = dict()

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
            source, name, catego = res

            print(f"[bold]Source found:[/bold] [italic]{source}[/italic]")

            print(f"[bold]Type found:[/bold] [italic]{catego}[/italic]")

            # Option de renommage
            catego = Prompt.ask(f"Entrez le type pour '{name}' (laisser vide pour ignorer)", default="")

            if catego and catego != name:
                PENDING_REcategoS[name] = (source, catego)

                print(f"[yellow]✔ Type '{catego}' sauvegardé en mémoire.[/yellow]")
        else:
            print(f"[red]Palette '{query}' introuvable.[/red]")

if __name__ == "__main__":
    if not SQLITE_DB_FILE.exists():
        print(f"[bold red]Erreur: DB introuvable à {SQLITE_DB_FILE}[/bold red]")
    else:
        run_app()
