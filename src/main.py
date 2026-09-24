#!/usr/bin/env python3
"""
main.py — Point d'entrée principal.

Lance le flux interactif :
  1. Sélection de l'exécutable llama-server
  2. Sélection du modèle .gguf (navigation ↑↓)
  3. Configuration des paramètres (navigation ↑↓)
     → Chargement automatique des derniers paramètres depuis models/settings.json
  4. Aperçu de la commande + confirmation
  5. Sauvegarde des paramètres dans models/settings.json
  6. Lancement du serveur
"""

import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.rule import Rule

console = Console()


# ─── Installation des dépendances au premier lancement ──────────────────────

def ensure_deps() -> None:
    missing = []
    for pkg in ("rich", "gguf", "questionary"):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        console.print(f"  [yellow]Installation :[/yellow] {', '.join(missing)} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        console.print()


ensure_deps()

# Imports internes (après s'être assuré que les deps sont présentes)
import ui
from config import MODELS_DIRS
from discovery import find_models, find_server_executable
from server import build_command, launch_server
from settings import load_for_model, save_for_model

# ─── Point d'entrée ──────────────────────────────────────────────────────────

def main() -> None:
    ui.print_banner()

    # 1 — Sélection du serveur
    default_server = find_server_executable()
    server_path = ui.select_server(default_server)

    # 2 — Recherche et sélection du modèle
    console.print()
    console.print("  [dim]Recherche des modèles .gguf...[/dim]")
    models = find_models(MODELS_DIRS)
    if models:
        console.print(f"  [green]✔[/green] {len(models)} modèle(s) trouvé(s).")
    else:
        console.print("  [yellow]Aucun modèle trouvé automatiquement.[/yellow]")

    selected_model, gguf_info = ui.select_model(models)

    # 3 — Chargement des paramètres sauvegardés (ou defaults)
    params = load_for_model(selected_model)
    # Détecter si des paramètres personnalisés existent déjà pour ce modèle
    from config import DEFAULTS
    from settings import load_all
    model_key = Path(selected_model).name
    has_saved = model_key in load_all()

    # 4 — Configuration interactive
    params = ui.configure_params(params, gguf_info, saved_note=has_saved)

    # 5 — Aperçu de la commande
    cmd = build_command(server_path, selected_model, params)
    ui.show_command_preview(server_path, selected_model, params, cmd)

    # 6 — Confirmation et lancement
    if not ui.confirm_launch(params["host"], params["port"]):
        console.print("\n  [dim]Annulé.[/dim]\n")
        return

    # Sauvegarde des paramètres avant de lancer (même si le serveur plante)
    save_for_model(selected_model, params)
    console.print(
        f"  [dim]Paramètres sauvegardés pour[/dim] [bold]{Path(selected_model).name}[/bold]"
    )
    console.print()

    launch_server(server_path, selected_model, params)

    console.print()
    console.print(Rule(style="dim"))
    console.print("[dim]  Session terminée.[/dim]\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n  [yellow]⚠[/yellow]  Interrompu.\n")
