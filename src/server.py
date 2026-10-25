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


def build_command(
    server: str, model: str, params: dict, routing_mode_enabled: bool = False
) -> list[str]:
    """
    Construct an argument list for subprocess
    """
    cmd = [server]

    if not routing_mode_enabled:
        cmd.extend(["-m", str(model)])
    else:
        cmd.extend(["--models-dir", str(MODELS_DIRS[0])])

    cmd.extend(["-ngl", str(params["ngl"])])
    cmd.extend(["-c", str(params["ctx"])])
    cmd.extend(["--threads", str(params["threads"])])
    cmd.extend(["--host", params["host"]])
    cmd.extend(["--port", str(params["port"])])
    cmd.extend(["--split-mode", params["split_mode"]])
    cmd.append("--ui-mcp-proxy")

    # --ctx-shift est actif par défaut dans les versions récentes de llama.cpp ;
    # on le désactive explicitement en mode "truncate".
    if params.get("ctx_mode") == "truncate":
        cmd.append("--no-context-shift")

    return cmd


def launch_server(cmd: list, params: dict) -> None:
    """
    Launch the server into a subprocess by using cmd string.
    """
    console.print(
        Panel(
            f"[dim]  Commande : {' '.join(cmd)}/dim\n\n"
            f"[bold yellow]⚡ Démarrage sur http://{params['host']}:{params['port']}[/bold yellow]\n"
            "[dim]Appuyez sur Ctrl+C pour arrêter[/dim]",
            border_style="yellow",
            box=box.HEAVY,
        )
    )
    console.print()
    try:
        subprocess.run(" ".join(cmd), check=False)
    except KeyboardInterrupt:
        console.print("\n\n  [yellow]⚠[/yellow]  Serveur arrêté par l'utilisateur.")
    except FileNotFoundError:
        console.print(
            f"\n  [red]✘[/red]  Exécutable introuvable : [bold]{cmd[0]}[/bold]\n"
            "  Vérifiez le chemin vers llama-server.exe"
        )
    except Exception as e:  # noqa: BLE001
        console.print(f"\n  [red]✘[/red]  Erreur : {e}")
