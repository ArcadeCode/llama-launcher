"""
Wikipedia MCP server.
No API key required — uses the Wikipedia REST API.
"""

import httpx

WIKI_API = "https://en.wikipedia.org/api/rest_v1"
WIKI_SEARCH = "https://en.wikipedia.org/w/api.php"


async def wikipedia_search(query: str, limit: int = 5) -> str:
    """Search Wikipedia for articles matching a query.

    Args:
        query: Search terms
        limit: Number of results to return (1-10, default 5)
    """
    limit = min(max(1, limit), 10)
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            WIKI_SEARCH,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": limit,
                "format": "json",
            },
        )
        r.raise_for_status()
        data = r.json()

    results = []
    for item in data.get("query", {}).get("search", []):
        import re

        snippet = re.sub(r"<[^>]+>", "", item.get("snippet", ""))
        results.append(
            f"**{item['title']}**\n{snippet}\nhttps://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}"
        )
    return "\n\n".join(results) if results else f"No Wikipedia results for '{query}'."


async def wikipedia_summary(title: str) -> str:
    """Get a concise summary of a Wikipedia article.

    Args:
        title: The exact Wikipedia article title (e.g. 'Python (programming language)')
    """
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"{WIKI_API}/page/summary/{title.replace(' ', '_')}",
            headers={"User-Agent": "mcp-everything/0.1.0"},
        )
        if r.status_code == 404:
            return (
                f"No Wikipedia article found for '{title}'. Try wikipedia_search first."
            )
        r.raise_for_status()
        data = r.json()

    lines = [
        f"# {data.get('title')}",
        f"*{data.get('description', '')}*",
        "",
        data.get("extract", "No summary available."),
        "",
        f"Read more: {data.get('content_urls', {}).get('desktop', {}).get('page', '')}",
    ]
    return "\n".join(lines)


async def wikipedia_random() -> str:
    """Get a random Wikipedia article summary — great for discovering interesting topics."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"{WIKI_API}/page/random/summary",
            headers={"User-Agent": "mcp-everything/0.1.0"},
        )
        r.raise_for_status()
        data = r.json()

    return (
        f"# {data.get('title')}\n"
        f"*{data.get('description', '')}*\n\n"
        f"{data.get('extract', '')}\n\n"
        f"Read more: {data.get('content_urls', {}).get('desktop', {}).get('page', '')}"
    )


async def wikipedia_on_this_day(
    month: int | None = None, day: int | None = None
) -> str:
    """Get notable events that happened on a given date in history.

    Args:
        month: Month number (1-12). Defaults to today.
        day: Day number (1-31). Defaults to today.
    """
    if month is None or day is None:
        from datetime import date

        today = date.today()
        month = month or today.month
        day = day or today.day

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"{WIKI_API}/feed/onthisday/events/{month}/{day}",
            headers={"User-Agent": "mcp-everything/0.1.0"},
        )
        r.raise_for_status()
        data = r.json()

    events = data.get("events", [])[:5]
    results = [f"**On This Day — {month}/{day}**\n"]
    for event in events:
        results.append(f"• **{event.get('year')}**: {event.get('text', '')}")
    return "\n".join(results) if results else "No events found for this date."


TOOLS = [wikipedia_search, wikipedia_summary, wikipedia_random, wikipedia_on_this_day]
