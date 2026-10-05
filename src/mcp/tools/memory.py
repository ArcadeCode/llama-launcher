"""
memory.py — Minimalist memory: a list of facts stored as JSON.

No vector database, no semantic search: for occasional use with a context
of a few thousand tokens, we simply inject every memory into the system
prompt. The model can add some through the "remember" tool (see
tools/remember.py).

This module is shared: the MCP server uses it to write, and your chat
client can import it for `as_prompt_block()` (same JSON file).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from config import MEMORY_PATH, TZ_OFFSET


def _load() -> list[dict]:
    if not Path(MEMORY_PATH).exists():
        return []
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError, OSError:
        return []


def _save(entries: list[dict]) -> None:
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def add(text: str) -> int:
    entries = _load()
    new_id = (max((e["id"] for e in entries), default=0)) + 1
    entries.append(
        {
            "id": new_id,
            "text": text,
            "created_at": datetime.now(tz=timezone.UTC + TZ_OFFSET).isoformat(
                timespec="seconds"
            ),
        }
    )
    _save(entries)
    return new_id


def forget(entry_id: int) -> bool:
    entries = _load()
    remaining = [e for e in entries if e["id"] != entry_id]
    if len(remaining) == len(entries):
        return False
    _save(remaining)
    return True


def all_entries() -> list[dict]:
    return _load()


def as_prompt_block() -> str:
    """Format memory for injection into the system prompt. Empty string if nothing is stored."""
    entries = _load()
    if not entries:
        return ""
    lines = [f"- (#{e['id']}) {e['text']}" for e in entries]
    return "Stored memories (usable as context):\n" + "\n".join(lines)
