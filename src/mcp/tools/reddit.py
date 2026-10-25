"""
Reddit MCP server.
No API key required for read-only access via Reddit's public JSON endpoints.
"""

import httpx

HEADERS = {"User-Agent": "mcp-everything/0.1.0 (github.com/Wellix260/mcp-everything)"}


async def _get(url: str, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(
        timeout=12, headers=HEADERS, follow_redirects=True
    ) as client:
        r = await client.get(url, params=params or {})
        r.raise_for_status()
        return r.json()


def _fmt_post(post: dict, index: int | None = None) -> str:
    d = post.get("data", {})
    prefix = f"{index}. " if index is not None else "• "
    title = d.get("title", "Untitled")
    subreddit = d.get("subreddit_name_prefixed", "")
    score = d.get("score", 0)
    comments = d.get("num_comments", 0)
    author = d.get("author", "unknown")
    url = d.get("url", "")
    permalink = f"https://reddit.com{d.get('permalink', '')}"
    selftext = d.get("selftext", "")[:200]
    is_self = d.get("is_self", False)

    lines = [
        f"{prefix}**{title}** ({subreddit})",
        f"   ⬆️ {score:,} | 💬 {comments} | by u/{author}",
    ]
    if selftext and is_self:
        lines.append(f"   _{selftext.strip()}..._")
    else:
        lines.append(f"   🔗 {url}")
    lines.append(f"   {permalink}")
    return "\n".join(lines)


async def reddit_hot(subreddit: str = "all", limit: int = 10) -> str:
    """Get hot posts from a subreddit or r/all.

    Args:
        subreddit: Subreddit name without 'r/' (e.g. 'python', 'technology', 'all')
        limit: Number of posts (1-25, default 10)
    """
    limit = min(max(1, limit), 25)
    data = await _get(
        f"https://www.reddit.com/r/{subreddit}/hot.json", {"limit": limit}
    )
    posts = data.get("data", {}).get("children", [])
    if not posts:
        return (
            f"No posts found in r/{subreddit}. Make sure the subreddit name is correct."
        )

    results = [f"**Hot posts in r/{subreddit}**\n"]
    for i, post in enumerate(posts, 1):
        results.append(_fmt_post(post, i))
    return "\n\n".join(results)


async def reddit_search(
    query: str, subreddit: str = "", limit: int = 5, sort: str = "relevance"
) -> str:
    """Search Reddit posts.

    Args:
        query: Search terms
        subreddit: Limit search to a specific subreddit (optional, e.g. 'python')
        limit: Number of results (1-25, default 5)
        sort: 'relevance', 'hot', 'top', 'new' (default 'relevance')
    """
    limit = min(max(1, limit), 25)
    base = (
        f"https://www.reddit.com/r/{subreddit}/search.json"
        if subreddit
        else "https://www.reddit.com/search.json"
    )
    params = {"q": query, "limit": limit, "sort": sort, "restrict_sr": bool(subreddit)}
    data = await _get(base, params)
    posts = data.get("data", {}).get("children", [])
    if not posts:
        scope = f"r/{subreddit}" if subreddit else "Reddit"
        return f"No results for '{query}' on {scope}."

    results = [f"**Reddit search: '{query}'**\n"]
    for i, post in enumerate(posts, 1):
        results.append(_fmt_post(post, i))
    return "\n\n".join(results)


async def reddit_top(subreddit: str, time_filter: str = "week", limit: int = 5) -> str:
    """Get top posts from a subreddit for a given time period.

    Args:
        subreddit: Subreddit name without 'r/' (e.g. 'MachineLearning', 'programming')
        time_filter: 'day', 'week', 'month', 'year', 'all' (default 'week')
        limit: Number of posts (1-25, default 5)
    """
    limit = min(max(1, limit), 25)
    tf = (
        time_filter
        if time_filter in ("hour", "day", "week", "month", "year", "all")
        else "week"
    )
    data = await _get(
        f"https://www.reddit.com/r/{subreddit}/top.json", {"limit": limit, "t": tf}
    )
    posts = data.get("data", {}).get("children", [])
    if not posts:
        return f"No top posts found in r/{subreddit}."

    results = [f"**Top posts in r/{subreddit} (this {tf})**\n"]
    for i, post in enumerate(posts, 1):
        results.append(_fmt_post(post, i))
    return "\n\n".join(results)


async def reddit_comments(post_url: str, limit: int = 5) -> str:
    """Get top comments from a Reddit post.

    Args:
        post_url: Full URL of the Reddit post (e.g. https://reddit.com/r/python/comments/abc123/...)
        limit: Number of top-level comments (1-15, default 5)
    """
    limit = min(max(1, limit), 15)
    # Convert to JSON endpoint
    clean = post_url.rstrip("/")
    if not clean.endswith(".json"):
        clean += ".json"
    data = await _get(clean, {"limit": limit})
    if not isinstance(data, list) or len(data) < 2:
        return "Could not load comments for that URL."

    comments = data[1].get("data", {}).get("children", [])[:limit]
    results = []
    for c in comments:
        d = c.get("data", {})
        if d.get("kind") == "more" or not d.get("body"):
            continue
        body = d.get("body", "").strip()[:400]
        author = d.get("author", "unknown")
        score = d.get("score", 0)
        results.append(f"**u/{author}** ⬆️ {score}\n{body}")

    return "\n\n---\n\n".join(results) if results else "No comments found."


TOOLS = [reddit_hot, reddit_search, reddit_top, reddit_comments]
