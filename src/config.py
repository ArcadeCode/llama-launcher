"""
config.py - Constants & defaults paths
"""

from pathlib import Path

# Fallback default model settings
DEFAULTS: dict = {
    "ngl": 100,
    "ctx": 4096,
    "threads": 7,
    "host": "0.0.0.0",
    "port": 8080,
    "split_mode": "layer",
    "ctx_mode": "truncate",  # "truncate" | "rolling"
}

SPLIT_MODES: list[str] = ["layer", "row", "none"]

# ─── Chemins de recherche ────────────────────────────────────────────────────

LLAMA_SERVER_PATHS: list[str] = [
    r"C:/Users/Utilisateur/Desktop/llama/llama.cpp/build/bin/llama-server.exe",
    r"C:/Users/Utilisateur/Desktop/llama/llama.cpp/build/bin/llama-server",
    "./llama.cpp/build/bin/llama-server",
    "./build/bin/llama-server",
    "llama-server",
]

# TODO: Take of MODELS_DIRS and replace it by an MODEL dir no multiples folders.
MODELS_DIRS: list[str] = [
    r"C:/Users/Utilisateur/Desktop/llama/models",
    # r"C:/Users/Utilisateur/Desktop/llama",
    # "./models",
    # ".",
]

# Répertoire où est stocké settings.json (relatif au script principal)
SETTINGS_DIR: Path = Path(MODELS_DIRS[0])
SETTINGS_FILE: Path = SETTINGS_DIR / Path("settings.json")

MEMORY_PATH: Path = Path(MODELS_DIRS[0] / Path("memory.json"))

TZ_OFFSET: int = +2  # Central European Summer Time

# Dossiers qui trahissent un dépôt source llama.cpp — on exclut tout .gguf
# dont le chemin traverse l'un d'eux.
SOURCE_MARKERS: frozenset[str] = frozenset(
    {
        "llama.cpp",
        "build",
        "cmake",
        "src",
        "tests",
        "examples",
        "common",
        "ggml",
        ".git",
        "scripts",
        "ci",
    }
)
