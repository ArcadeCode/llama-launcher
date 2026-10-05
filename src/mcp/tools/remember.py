"""
tools/remember.py — Give the model control over persistent memory
(memory.py), so it can remember, list or forget facts on its own.
"""

from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field

from tools import memory


def remember(
    text: Annotated[
        str,
        Field(
            description="The fact to remember, formulated independently and concisely."
        ),
    ],
) -> str:
    """Records a durable fact to remember for upcoming conversations
    (user preference, useful recurring information, decision made).
    Don't use for temporary or obvious information."""
    if not text.strip():
        raise ToolError("Cannot remember an empty text.")
    new_id = memory.add(text.strip())
    return f"Remembered (#{new_id}): {text.strip()}"


def list_memories() -> str:
    """Lists all recorded memories with their number (#id).
    Use it to find the id of a memory before deleting it with `forget`."""
    entries = memory.all_entries()
    if not entries:
        return "No memories recorded."
    return "\n".join(f"- (#{e['id']}) {e['text']}" for e in entries)


def forget(
    entry_id: Annotated[
        int, Field(description="The identifier (#id) of the memory to delete.")
    ],
) -> str:
    """Deletes a previously recorded memory by its number (#id)."""
    if memory.forget(entry_id):
        return f"Memory #{entry_id} deleted."
    return f"No memory #{entry_id} found."


TOOLS = [remember, list_memories, forget]
