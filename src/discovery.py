"""
discovery.py - Search for llama-server executable and .gguf files
"""

from __future__ import annotations

from pathlib import Path

from config import LLAMA_SERVER_PATHS, MODELS_DIRS, SOURCE_MARKERS


def find_server_executable() -> str | None:
    """Return the first `llama-server` executable found or None in case of failure"""
    for path in LLAMA_SERVER_PATHS:
        if Path(path).exists():
            return str(path)
    return None


def _is_in_source_tree(path: Path) -> bool:
    """Retourne True si le fichier est vraisemblablement dans un dépôt source."""
    return any(part in SOURCE_MARKERS for part in path.parts)


def find_models(dirs: list[str] | None = None) -> list[Path]:
    """
    Cherche récursivement tous les .gguf dans les répertoires donnés.
    Exclut les fichiers situés dans un arbre source llama.cpp.
    """
    if dirs is None:
        dirs = MODELS_DIRS

    models: list[Path] = []
    seen: set[Path] = set()

    for d in dirs:
        p = Path(d)
        if not (p.exists() and p.is_dir()):
            continue
        for f in sorted(p.rglob("*.gguf")):
            if f in seen:
                continue
            seen.add(f)
            if _is_in_source_tree(f):
                continue
            models.append(f)

    return models
