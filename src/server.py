"""
server.py — Construction de la commande llama-server et lancement du processus.
"""

from __future__ import annotations

import subprocess

from rich import box
from rich.console import Console
from rich.panel import Panel

from config import MODELS_DIRS

console = Console()


def build_command(server: str, model: str, params: dict, enable_jinja: bool = True, enable_model_routing: bool = False) -> list[str]:
    """Construit la liste d'arguments pour subprocess."""
    cmd = [
        server,
        "-m", str(model),
        "-ngl", str(params["ngl"]),
        "-c", str(params["ctx"]),
        "--threads", str(params["threads"]),
        "--host", params["host"],
        "--port", str(params["port"]),
        "--split-mode", params["split_mode"],
    ]
    # --ctx-shift est actif par défaut dans les versions récentes de llama.cpp ;
    # on le désactive explicitement en mode "truncate".
    if params.get("ctx_mode") == "truncate":
        cmd.append("--no-context-shift")

    if enable_jinja and not enable_model_routing: # For some reason, jinja and model routing are incompatible
        cmd.append("--jinja")

    if enable_model_routing:
        # Overwrite the -m argument.
        cmd[1] = "--models-dir", str(MODELS_DIRS[0]),

    return cmd

def launch_server(server: str, model: str, params: dict) -> None:
    cmd = build_command(server, model, params)
    console.print(Panel(
        f"[bold yellow]⚡ Démarrage sur http://{params['host']}:{params['port']}[/bold yellow]\n"
        "[dim]Appuyez sur Ctrl+C pour arrêter[/dim]",
        border_style="yellow",
        box=box.HEAVY,
    ))
    console.print()
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        console.print("\n\n  [yellow]⚠[/yellow]  Serveur arrêté par l'utilisateur.")
    except FileNotFoundError:
        console.print(
            f"\n  [red]✘[/red]  Exécutable introuvable : [bold]{server}[/bold]\n"
            "  Vérifiez le chemin vers llama-server.exe"
        )
    except Exception as e:  # noqa: BLE001
        console.print(f"\n  [red]✘[/red]  Erreur : {e}")
