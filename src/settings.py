"""
settings.py — Persistance des paramètres par modèle dans models/settings.json.

Structure du fichier :
{
    "nom_du_fichier.gguf": {
        "ngl": 100,
        "ctx": 8192,
        ...
    },
    ...
}
"""

import json
from pathlib import Path

from config import DEFAULTS, SETTINGS_FILE


def _ensure_file() -> None:
    """Crée le fichier settings.json s'il n'existe pas."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not SETTINGS_FILE.exists():
        SETTINGS_FILE.write_text("{}\n", encoding="utf-8")


def load_all() -> dict:
    """Retourne le contenu complet de settings.json (dict vide si absent/corrompu)."""
    _ensure_file()
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_for_model(model_path: str) -> dict:
    """
    Retourne les paramètres enregistrés pour ce modèle.
    Clé = nom de fichier seul (sans répertoire).
    Fusionne avec DEFAULTS pour garantir que toutes les clés sont présentes.
    """
    key = Path(model_path).name
    all_settings = load_all()
    saved = all_settings.get(key, {})
    # DEFAULTS en base, paramètres sauvegardés par-dessus
    merged = dict(DEFAULTS)
    merged.update({k: v for k, v in saved.items() if k in DEFAULTS})
    return merged


def save_for_model(model_path: str, params: dict) -> None:
    """
    Enregistre les paramètres du modèle dans settings.json.
    Clé = nom de fichier seul.
    """
    _ensure_file()
    key = Path(model_path).name
    all_settings = load_all()
    all_settings[key] = {k: v for k, v in params.items() if k in DEFAULTS}
    try:
        SETTINGS_FILE.write_text(
            json.dumps(all_settings, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except Exception as e:
        # Non bloquant : on prévient sans planter
        print(f"  [Avertissement] Impossible de sauvegarder les paramètres : {e}")
