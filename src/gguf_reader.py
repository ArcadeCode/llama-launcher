"""
gguf_reader.py — Lecture des métadonnées depuis un fichier GGUF.
"""

from __future__ import annotations


def read_gguf_info(model_path: str) -> dict:
    """
    Lit plusieurs métadonnées utiles du GGUF.

    Retourne un dict avec les clés disponibles parmi :
        ctx_length, embedding, layers, heads, name, arch
    """
    info: dict = {}
    int_keys = {
        "llama.context_length":       "ctx_length",
        "llama.embedding_length":     "embedding",
        "llama.block_count":          "layers",
        "llama.attention.head_count": "heads",
    }
    str_keys = {
        "general.name":         "name",
        "general.architecture": "arch",
    }
    try:
        from gguf import GGUFReader
        reader = GGUFReader(str(model_path), mode="r")

        for gguf_key, short_key in int_keys.items():
            field = reader.get_field(gguf_key)
            if field and len(field.parts) > 0:
                try:
                    info[short_key] = int(field.parts[-1])
                except Exception:
                    pass

        for gguf_key, short_key in str_keys.items():
            field = reader.get_field(gguf_key)
            if field and len(field.parts) > 0:
                try:
                    info[short_key] = "".join(
                        p.tobytes().decode("utf-8", errors="replace")
                        for p in field.parts
                        if hasattr(p, "tobytes")
                    ).strip("\x00").strip()
                except Exception:
                    pass
    except Exception:
        pass

    return info
