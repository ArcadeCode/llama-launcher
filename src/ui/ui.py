"""
ui.py — Interface utilisateur : affichage Rich + sélections au clavier (questionary).

Toutes les interactions avec l'utilisateur passent par ce module.
"""

from __future__ import annotations

from pathlib import Path

import questionary
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from config import SPLIT_MODES
from utils import format_size_from_path, q

from .response import SelectedModelResponseType

console = Console()

# ─── Bannière ────────────────────────────────────────────────────────────────


def print_banner() -> None:
    console.print()
    title = Text()
    title.append("⚡ ", style="bold yellow")
    title.append("llama.cpp", style="bold cyan")
    title.append(" Server Launcher", style="bold white")
    console.print(
        Panel(
            title,
            subtitle="[dim]Gestionnaire de démarrage interactif[/dim]",
            border_style="cyan",
            padding=(0, 2),
            box=box.DOUBLE_EDGE,
        )
    )
    console.print()


# ─── Sélection du serveur ────────────────────────────────────────────────────


def select_server(default_server: str | None) -> str:
    console.print(Rule("[bold cyan]Exécutable llama-server[/bold cyan]", style="cyan"))
    console.print()

    if default_server:
        console.print(f"  [green]✔[/green] Trouvé : [bold]{default_server}[/bold]")
        use_default = q(
            questionary.select,
            "  Utiliser ce chemin ?",
            choices=[
                questionary.Choice(title="Oui", value=True),
                questionary.Choice(title="Non — saisir un autre chemin", value=False),
            ],
            instruction="(↑↓ + Entrée)",
        )
        if use_default:
            return default_server

    return q(
        questionary.text,
        "  Chemin vers llama-server",
        default=default_server or "llama-server",
    )


# ─── Sélection du modèle ────────────────────────────────────────────────────


def select_model(
    models: list[Path],
) -> tuple[SelectedModelResponseType, str, dict]:
    """
    Affiche la liste des modèles avec navigation au clavier.
    Retourne (chemin_modele, gguf_info).
    """
    from gguf_reader import read_gguf_info  # import local pour éviter cycle

    console.print()
    console.print(Rule("[bold cyan]Sélection du modèle[/bold cyan]", style="cyan"))
    console.print()

    if not models:
        console.print(
            "  [yellow]⚠[/yellow]  Aucun fichier .gguf trouvé dans les dossiers par défaut."
        )
        path = q(questionary.text, "  Entrez le chemin complet du modèle")
        info = read_gguf_info(path)
        return path, info

    # Construction des choix : label affiché = "nom.gguf  (taille)"
    # TODO: Edit by making this an table and adding Parameter count.
    MANUAL = "── Saisir un chemin manuellement... ──"
    ROUTING_MODE = "Enable routing mode..."

    choices = (
        [
            questionary.Choice(
                title=f"{m.name}  ({format_size_from_path(m)})",
                value=str(m),
            )
            for m in models
        ]
        + [questionary.Choice(title=ROUTING_MODE, value=ROUTING_MODE)]
        + [questionary.Choice(title=MANUAL, value=MANUAL)]
    )

    selected_value = q(
        questionary.select,
        "  Choisissez un modèle",
        choices=choices,
        use_shortcuts=False,
        instruction="(↑↓ pour naviguer, Entrée pour valider)",
    )

    if selected_value == MANUAL:
        model_path = q(questionary.text, "  Chemin complet du modèle")
        response_type = SelectedModelResponseType.MANUAL

    elif selected_value == ROUTING_MODE:
        model_path = None
        info = {}
        response_type = SelectedModelResponseType.ROUTING

    else:
        model_path = selected_value
        response_type = SelectedModelResponseType.MODEL

    if selected_value != ROUTING_MODE:
        console.print("\n  [dim]Lecture des métadonnées...[/dim]")
        info = read_gguf_info(model_path)

        arch = info.get("arch", "?")
        name = info.get("name", Path(model_path).stem)
        console.print(f"  [green]✔[/green] [bold]{name}[/bold]  [dim]{arch}[/dim]")
        if "ctx_length" in info:
            console.print(
                f"  [dim]Contexte natif du modèle :[/dim] "
                f"[bold cyan]{info['ctx_length']:,}[/bold cyan] tokens"
            )

    return response_type, model_path, info


# ─── Configuration des paramètres ───────────────────────────────────────────

_PARAM_INFO = [
    ("ngl", "GPU Layers (-ngl)", "Couches chargées sur GPU (100 = tout)"),
    ("ctx", "Context size (-c)", "Taille du contexte en tokens"),
    ("threads", "Threads CPU", "Nombre de threads CPU à utiliser"),
    ("host", "Host", "Adresse d'écoute (0.0.0.0 = toutes interfaces)"),
    ("port", "Port", "Port HTTP du serveur"),
    ("split_mode", "Split mode", f"Répartition GPU : {'/'.join(SPLIT_MODES)}"),
    (
        "ctx_mode",
        "Mode contexte",
        "truncate = erreur si dépassement | rolling = oubli du début",
    ),
]

DONE_SENTINEL = "__done__"


def _params_table(params: dict, gguf_ctx: int | None) -> None:
    """Affiche le tableau récapitulatif des paramètres courants."""
    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.SIMPLE_HEAVY,
        padding=(0, 1),
    )
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Paramètre", style="bold white", width=22)
    table.add_column("Valeur", style="cyan", justify="right")
    table.add_column("Description", style="dim")

    for i, (key, label, desc) in enumerate(_PARAM_INFO, 1):
        val = str(params[key])
        if key == "ctx_mode":
            val_display = (
                "[bold green]rolling (--ctx-shift)[/bold green]"
                if params[key] == "rolling"
                else "[yellow]truncate[/yellow]"
            )
        elif key == "ctx" and gguf_ctx and params[key] == gguf_ctx:
            val_display = f"[bold cyan]{val}[/bold cyan] [dim](recommandé GGUF)[/dim]"
        else:
            val_display = val
        table.add_row(str(i), label, val_display, desc)

    console.print(table)


def configure_params(current: dict, gguf_info: dict, saved_note: bool = False) -> dict:
    """
    Dialogue interactif de configuration des paramètres.
    Retourne le dict params (potentiellement modifié).
    """
    console.print()
    console.print(Rule("[bold cyan]Paramètres de lancement[/bold cyan]", style="cyan"))
    console.print()

    # Appliquer le ctx GGUF comme valeur par défaut
    gguf_ctx: int | None = gguf_info.get("ctx_length")
    if isinstance(gguf_ctx, int) and gguf_ctx > 0:
        current["ctx"] = gguf_ctx
        console.print(
            f"  [green]✔[/green] Context size depuis les métadonnées GGUF : "
            f"[bold cyan]{gguf_ctx:,}[/bold cyan] tokens"
        )

    if saved_note:
        console.print(
            "  [dim]↩  Paramètres chargés depuis la session précédente.[/dim]"
        )

    console.print()
    _params_table(current, gguf_ctx)
    console.print()

    wants_edit = q(
        questionary.select,
        "  Modifier des paramètres ?",
        choices=[
            questionary.Choice(title="Non — garder ces valeurs", value=False),
            questionary.Choice(title="Oui — modifier", value=True),
        ],
        instruction="(↑↓ + Entrée)",
    )
    if not wants_edit:
        return current

    updated = dict(current)

    # Choix du paramètre à modifier par flèches
    while True:
        console.print()
        param_choices = [
            questionary.Choice(
                title=f"{label:<22}  {str(updated[key]):<15}  {desc}",
                value=key,
            )
            for key, label, desc in _PARAM_INFO
        ] + [
            questionary.Choice(
                title="✔  Terminer les modifications", value=DONE_SENTINEL
            )
        ]

        chosen_key = q(
            questionary.select,
            "  Paramètre à modifier",
            choices=param_choices,
            instruction="(↑↓ pour naviguer, Entrée pour valider)",
        )

        if chosen_key == DONE_SENTINEL:
            break

        # Trouver le label correspondant
        label = next(l for k, l, _ in _PARAM_INFO if k == chosen_key)
        current_val = updated[chosen_key]

        if chosen_key == "split_mode":
            new_val = q(
                questionary.select,
                f"  {label}",
                choices=SPLIT_MODES,
                default=current_val,
            )
            updated[chosen_key] = new_val

        elif chosen_key == "ctx_mode":
            new_val = q(
                questionary.select,
                f"  {label}",
                choices=[
                    questionary.Choice(
                        title="truncate  — erreur si le prompt dépasse le contexte",
                        value="truncate",
                    ),
                    questionary.Choice(
                        title="rolling   — oublie silencieusement le début (--ctx-shift)",
                        value="rolling",
                    ),
                ],
                default=current_val,
            )
            updated[chosen_key] = new_val

        elif isinstance(current_val, int):
            raw = q(
                questionary.text,
                f"  {label}",
                default=str(current_val),
                validate=lambda v: v.isdigit() or "Entrez un nombre entier.",
            )
            updated[chosen_key] = int(raw)

        else:
            new_val = q(
                questionary.text,
                f"  {label}",
                default=str(current_val),
            )
            updated[chosen_key] = new_val

        console.print(
            f"  [green]✔[/green] {label} → [bold cyan]{updated[chosen_key]}[/bold cyan]"
        )

    return updated


# ─── Récapitulatif avant lancement ──────────────────────────────────────────


def show_command_preview(
    server: str,
    routing_mode: bool,
    params: dict,
    cmd: list[str],
    model: str | None = None,
) -> None:
    console.print()
    console.print(Rule("[bold cyan]Récapitulatif[/bold cyan]", style="cyan"))
    console.print()

    cmd_str = " \\\n    ".join(cmd)
    console.print(
        Panel(
            f"[bold green]{cmd_str}[/bold green]",
            title="[bold]Commande générée[/bold]",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print()

    info_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    info_table.add_column(style="dim")
    info_table.add_column(style="bold white")
    if routing_mode:
        info_table.add_row("Routing mode", "enabled")
    else:
        info_table.add_row("Modèle", Path(model).name)
    info_table.add_row("GPU Layers", str(params["ngl"]))
    info_table.add_row("Contexte", "Define for each model")
    info_table.add_row("Threads", str(params["threads"]))
    info_table.add_row("Serveur", f"http://{params['host']}:{params['port']}")
    info_table.add_row("Split mode", params["split_mode"])
    info_table.add_row(
        "Mode contexte",
        "[bold green]rolling (oubli du début)[/bold green]"
        if params.get("ctx_mode") == "rolling"
        else "[yellow]truncate (erreur si dépassement)[/yellow]",
    )
    console.print(info_table)
    console.print()


# ─── Confirmation finale ─────────────────────────────────────────────────────


def confirm_launch(host: str, port: int) -> bool:
    return q(
        questionary.select,
        f"  Lancer le serveur sur http://{host}:{port} ?",
        choices=[
            questionary.Choice(title="Oui — lancer", value=True),
            questionary.Choice(title="Non — annuler", value=False),
        ],
        instruction="(↑↓ + Entrée)",
    )
