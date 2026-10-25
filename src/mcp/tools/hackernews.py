"""
Hacker News MCP server.
No API key required — uses the official HN Firebase API.
"""

import httpx

HN_API = "https://hacker-news.firebaseio.com/v0"
ALGOLIA_API = "https://hn.algolia.com/api/v1"


async def _get(url: str) -> dict | list:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()


async def hn_top_stories(limit: int = 10) -> str:
    """Get the current top stories from Hacker News.

    Args:
        limit: Number of stories to return (1-30, default 10)
    """
    limit = min(max(1, limit), 30)
    ids = await _get(f"{HN_API}/topstories.json")
    stories = []
    for item_id in ids[:limit]:
        item = await _get(f"{HN_API}/item/{item_id}.json")
        if item and item.get("type") == "story":
            stories.append(
                f"• [{item.get('title')}]({item.get('url', f'https://news.ycombinator.com/item?id={item_id}')})\n"
                f"  {item.get('score', 0)} points | {item.get('descendants', 0)} comments | by {item.get('by', 'unknown')}"
            )
    return "\n\n".join(stories) if stories else "No stories found."


async def hn_search(query: str, limit: int = 5) -> str:
    """Search Hacker News stories and comments.

    Args:
        query: Search terms
        limit: Number of results (1-20, default 5)
    """
    limit = min(max(1, limit), 20)
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"{ALGOLIA_API}/search",
            params={"query": query, "hitsPerPage": limit, "tags": "story"},
        )
        r.raise_for_status()
        data = r.json()

    results = []
    for hit in data.get("hits", []):
        results.append(
            f"• {hit.get('title', 'Untitled')}\n"
            f"  {hit.get('points', 0)} points | {hit.get('num_comments', 0)} comments\n"
            f"  https://news.ycombinator.com/item?id={hit.get('objectID')}"
        )
    return "\n\n".join(results) if results else f"No results for '{query}'."


async def hn_get_comments(story_id: int, limit: int = 5) -> str:
    """Get top comments for a Hacker News story.

    Args:
        story_id: The HN item ID (found in the URL)
        limit: Number of top-level comments to return (1-20, default 5)
    """
    limit = min(max(1, limit), 20)
    item = await _get(f"{HN_API}/item/{story_id}.json")
    if not item:
        return f"Story {story_id} not found."

    kids = item.get("kids", [])[:limit]
    comments = []
    for kid_id in kids:
        comment = await _get(f"{HN_API}/item/{kid_id}.json")
        if comment and not comment.get("deleted") and not comment.get("dead"):
            text = comment.get("text", "").replace("<p>", "\n").replace("</p>", "")
            import re

            text = re.sub(r"<[^>]+>", "", text)
            comments.append(f"**{comment.get('by', 'unknown')}**: {text[:500]}")

    return "\n\n---\n\n".join(comments) if comments else "No comments found."


async def hn_ask_hn(limit: int = 5) -> str:
    """Get current 'Ask HN' posts — great for finding questions the community is discussing.

    Args:
        limit: Number of posts to return (1-20, default 5)
    """
    limit = min(max(1, limit), 20)
    ids = await _get(f"{HN_API}/askstories.json")
    results = []
    for item_id in ids[:limit]:
        item = await _get(f"{HN_API}/item/{item_id}.json")
        if item:
            results.append(
                f"• {item.get('title')}\n"
                f"  {item.get('score', 0)} points | {item.get('descendants', 0)} comments\n"
                f"  https://news.ycombinator.com/item?id={item_id}"
            )
    return "\n\n".join(results) if results else "No Ask HN posts found."


TOOLS = [hn_top_stories, hn_search, hn_get_comments, hn_ask_hn]
