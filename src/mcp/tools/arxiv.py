"""
ArXiv MCP server.
No API key required — uses the ArXiv public API.
"""

import xml.etree.ElementTree as ET

import httpx

ARXIV_API = "https://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _parse_entries(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    entries = []
    for entry in root.findall("atom:entry", NS):
        title = entry.findtext("atom:title", namespaces=NS) or ""
        summary = entry.findtext("atom:summary", namespaces=NS) or ""
        published = entry.findtext("atom:published", namespaces=NS) or ""
        link = ""
        for lnk in entry.findall("atom:link", NS):
            if lnk.get("type") == "text/html":
                link = lnk.get("href", "")
        authors = [
            a.findtext("atom:name", namespaces=NS) or ""
            for a in entry.findall("atom:author", NS)
        ]
        entries.append(
            {
                "title": title.strip().replace("\n", " "),
                "summary": summary.strip()[:500],
                "published": published[:10],
                "link": link,
                "authors": authors[:3],
            }
        )
    return entries


async def arxiv_search(query: str, limit: int = 5, category: str = "") -> str:
    """Search ArXiv for academic papers.

    Args:
        query: Search terms (e.g. 'large language models', 'quantum computing')
        limit: Number of papers to return (1-20, default 5)
        category: Optional ArXiv category filter (e.g. 'cs.AI', 'physics', 'math')
    """
    limit = min(max(1, limit), 20)
    search_query = f"all:{query}"
    if category:
        search_query = f"cat:{category} AND all:{query}"

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            ARXIV_API,
            params={
                "search_query": search_query,
                "max_results": limit,
                "sortBy": "relevance",
                "sortOrder": "descending",
            },
        )
        r.raise_for_status()
        entries = _parse_entries(r.text)

    if not entries:
        return f"No ArXiv papers found for '{query}'."

    results = []
    for p in entries:
        authors_str = ", ".join(p["authors"]) + (
            " et al." if len(p["authors"]) >= 3 else ""
        )
        results.append(
            f"**{p['title']}**\n"
            f"{authors_str} ({p['published']})\n"
            f"{p['summary']}...\n"
            f"{p['link']}"
        )
    return "\n\n---\n\n".join(results)


async def arxiv_recent(category: str = "cs.AI", limit: int = 5) -> str:
    """Get the most recent papers submitted to an ArXiv category.

    Args:
        category: ArXiv category (default 'cs.AI'). Popular: cs.AI, cs.LG, cs.CL, physics, math, q-bio
        limit: Number of papers to return (1-20, default 5)
    """
    limit = min(max(1, limit), 20)
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            ARXIV_API,
            params={
                "search_query": f"cat:{category}",
                "max_results": limit,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            },
        )
        r.raise_for_status()
        entries = _parse_entries(r.text)

    if not entries:
        return f"No recent papers found for category '{category}'."

    results = [f"**Recent papers in {category}**\n"]
    for p in entries:
        authors_str = ", ".join(p["authors"]) + (
            " et al." if len(p["authors"]) >= 3 else ""
        )
        results.append(
            f"• **{p['title']}** — {authors_str} ({p['published']})\n  {p['link']}"
        )
    return "\n\n".join(results)


async def arxiv_get_paper(arxiv_id: str) -> str:
    """Get full metadata for a specific ArXiv paper by its ID.

    Args:
        arxiv_id: The ArXiv paper ID (e.g. '2305.10403' or 'https://arxiv.org/abs/2305.10403')
    """
    # Handle full URLs
    arxiv_id = arxiv_id.strip()
    if "arxiv.org/abs/" in arxiv_id:
        arxiv_id = arxiv_id.split("arxiv.org/abs/")[-1]

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(ARXIV_API, params={"id_list": arxiv_id, "max_results": 1})
        r.raise_for_status()
        entries = _parse_entries(r.text)

    if not entries:
        return f"Paper '{arxiv_id}' not found."

    p = entries[0]
    return (
        f"# {p['title']}\n\n"
        f"**Authors:** {', '.join(p['authors'])}\n"
        f"**Published:** {p['published']}\n\n"
        f"**Abstract:**\n{p['summary']}\n\n"
        f"**Link:** {p['link']}"
    )


TOOLS = [arxiv_search, arxiv_recent, arxiv_get_paper]
