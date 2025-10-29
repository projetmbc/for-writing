#!/usr/bin/env python3
"""
Navigateur JSON interactif pour analyser les clés de 2ème niveau
Usage: python json_navigator.py <fichier.json>
"""
from pathlib import Path

THIS_DIR     = Path(__file__).parent
PROJECT_DIR  = THIS_DIR.parent
TOOLS_CONTRIB_DIR = PROJECT_DIR / "tools" / "01-contrib"

PAL_REPORT_FILE = TOOLS_CONTRIB_DIR / "pal-report.json"
MP_NAMES_FILE   = TOOLS_CONTRIB_DIR / "mp-names.json"

#!/usr/bin/env python3
"""
Navigateur JSON interactif pour analyser les clés de 2ème niveau
Usage: python json_navigator.py <fichier.json>
"""

import json
import sys
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box

console = Console()

def charger_json(file):
    """Charge le fichier JSON"""
    try:
        with file.open('r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Erreur: Fichier '{file}' introuvable[/red]")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]Erreur: JSON invalide - {e}[/red]")
        sys.exit(1)

def analyser_cles_niveau2(data):
    """Analyse et compte les clés de 2ème niveau"""
    cles_niveau2 = defaultdict(list)

    for cle_principale, contenu in data.items():
        if isinstance(contenu, dict):
            for cle_secondaire in contenu.keys():
                cles_niveau2[cle_secondaire].append(cle_principale)

    return dict(cles_niveau2)

def afficher_cles_disponibles(cles_niveau2):
    """Affiche les clés de 2ème niveau disponibles"""
    table = Table(title="Clés de 2ème niveau disponibles", box=box.ROUNDED)
    table.add_column("N°", style="cyan", justify="right")
    table.add_column("Clé", style="green")
    table.add_column("Occurrences", justify="right", style="yellow")

    for idx, (cle, occurences) in enumerate(sorted(cles_niveau2.items()), 1):
        table.add_row(str(idx), cle, str(len(occurences)))

    console.print(table)
    return list(sorted(cles_niveau2.keys()))

def afficher_resultats(data, cle_choisie, cles_principales):
    """Affiche les résultats pour la clé choisie, groupés par valeur"""
    console.print(f"\n[bold cyan]Entrées contenant la clé '{cle_choisie}':[/bold cyan]\n")

    # Grouper par valeur
    groupes = defaultdict(list)

    for cle_principale in cles_principales:
        valeur = data[cle_principale][cle_choisie]

        groupes[valeur].append(cle_principale)

    # Afficher chaque groupe
    for valeur, liste_cles in sorted(groupes.items()):
        # Créer le contenu du panel
        contenu = f"[dim]({len(liste_cles)} entrée(s))[/dim]\n\n"
        contenu += "[green]Clés de niveau 1:[/green]\n"

        # Afficher les clés groupées (max 10 par ligne)
        for i in range(0, len(liste_cles), 10):
            ligne = ", ".join(sorted(liste_cles[i:i+10]))
            contenu += f"  {ligne}\n"

        panel = Panel(contenu, title=f"[bold magenta]{cle_choisie}: {valeur}[/bold magenta]",
                     border_style="blue", box=box.ROUNDED)
        console.print(panel)

def main():
    # Charger le JSON
    console.print(f"[cyan]Chargement ciblé de {PAL_REPORT_FILE.name}...[/cyan]")

    mpnames = charger_json(MP_NAMES_FILE)
    _data = charger_json(PAL_REPORT_FILE)

    data = dict()

    for k in _data:
        if (
            k in mpnames
            and
            mpnames[k][-2:] == "_r"
        ):
            continue

        data[k] = _data[k]

    console.print(f"[green]✓ {len(data)} entrées principales trouvées[/green]\n")

    # Analyser les clés de niveau 2
    cles_niveau2 = analyser_cles_niveau2(data)

    if not cles_niveau2:
        console.print("[red]Aucune clé de 2ème niveau trouvée[/red]")
        sys.exit(1)

    # Afficher les clés disponibles
    liste_cles = afficher_cles_disponibles(cles_niveau2)

    # Demander le choix
    console.print("\n[bold]Options:[/bold]")
    console.print("  - Entrez un [cyan]numéro[/cyan] ou un [cyan]nom de clé[/cyan]")
    console.print("  - Tapez [yellow]'q'[/yellow] pour quitter\n")

    while True:
        choix = Prompt.ask("[bold green]Votre choix[/bold green]")

        if choix.lower() == 'q':
            console.print("[yellow]Au revoir![/yellow]")
            break

        # Vérifier si c'est un numéro
        cle_selectionnee = None
        if choix.isdigit():
            idx = int(choix) - 1
            if 0 <= idx < len(liste_cles):
                cle_selectionnee = liste_cles[idx]
        elif choix in cles_niveau2:
            cle_selectionnee = choix

        if cle_selectionnee:
            afficher_resultats(data, cle_selectionnee, cles_niveau2[cle_selectionnee])
            console.print("\n" + "="*60 + "\n")
            # Réafficher les clés disponibles
            afficher_cles_disponibles(cles_niveau2)
            console.print("\n[bold]Options:[/bold]")
            console.print("  - Entrez un [cyan]numéro[/cyan] ou un [cyan]nom de clé[/cyan]")
            console.print("  - Tapez [yellow]'q'[/yellow] pour quitter\n")
        else:
            console.print("[red]Choix invalide. Réessayez.[/red]\n")

if __name__ == "__main__":
    main()
