"""
tools/websearch.py — Web search without API key, via the `ddgs` package
(formerly duckduckgo-search).

pip install ddgs
"""

from typing import Annotated

from ddgs import DDGS
from fastmcp.exceptions import ToolError
from pydantic import Field


def web_search(
    query: Annotated[str, Field(description="The search query, short and targeted.")],
    max_results: Annotated[
        int, Field(ge=1, le=20, description="Number of results to return.")
    ] = 5,
) -> str:
    """Searches the web for current information or facts you don't know
    (news, recent versions, verifiable facts). Returns a list of results
    with title, url and excerpt."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:  # noqa: BLE001
        raise ToolError(f"Search failed: {e}") from e

    if not results:
        return f"No results for '{query}'."

    lines = [f"Results for '{query}':"]
    for i, r in enumerate(results, 1):
        title = r.get("title", "").strip()
        url = r.get("href", "").strip()
        body = r.get("body", "").strip()
        lines.append(f"{i}. {title}\n   {url}\n   {body}")
    return "\n".join(lines)


TOOLS = [web_search]
