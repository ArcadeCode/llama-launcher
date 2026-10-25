"""
Books MCP server.
No API key required — uses the Open Library API.
"""

import httpx

OL_API = "https://openlibrary.org"
COVERS_API = "https://covers.openlibrary.org"


async def books_search(query: str, limit: int = 5) -> str:
    """Search for books by title, author, or keyword.

    Args:
        query: Search terms (e.g. 'dune frank herbert', 'harry potter', 'machine learning')
        limit: Number of results (1-20, default 5)
    """
    limit = min(max(1, limit), 20)
    async with httpx.AsyncClient(timeout=12) as client:
        r = await client.get(
            f"{OL_API}/search.json",
            params={
                "q": query,
                "limit": limit,
                "fields": "title,author_name,first_publish_year,isbn,subject,ratings_average,editions_count",
            },
        )
        r.raise_for_status()
        data = r.json()

    docs = data.get("docs", [])
    if not docs:
        return f"No books found for '{query}'."

    total = data.get("numFound", 0)
    results = [f"**Book search: '{query}'** ({total:,} total)\n"]
    for doc in docs:
        authors = ", ".join(doc.get("author_name", [])[:3]) or "Unknown author"
        year = doc.get("first_publish_year", "?")
        rating = doc.get("ratings_average")
        rating_str = f"  ⭐ {rating:.1f}/5" if rating else ""
        editions = doc.get("editions_count", "?")
        subjects = ", ".join((doc.get("subject") or [])[:3])
        results.append(
            f"**{doc.get('title', 'Untitled')}**\n"
            f"  by {authors} ({year}){rating_str}\n"
            f"  {editions} editions | {subjects}"
        )
    return "\n\n".join(results)


async def books_author(author_name: str) -> str:
    """Look up an author and their most notable works.

    Args:
        author_name: Author's name (e.g. 'George Orwell', 'Ursula Le Guin')
    """
    async with httpx.AsyncClient(timeout=12) as client:
        # Search for the author
        r = await client.get(
            f"{OL_API}/search/authors.json",
            params={"q": author_name, "limit": 1},
        )
        r.raise_for_status()
        data = r.json()

    docs = data.get("docs", [])
    if not docs:
        return f"Author '{author_name}' not found."

    author = docs[0]
    author_key = author.get("key", "")
    name = author.get("name", author_name)
    birth = author.get("birth_date", "?")
    death = author.get("death_date", "")
    work_count = author.get("work_count", 0)
    top_subjects = ", ".join(author.get("top_subjects", [])[:5])
    top_work = author.get("top_work", "")

    lifespan = f"{birth}–{death}" if death else f"b. {birth}" if birth != "?" else ""

    lines = [
        f"# {name}",
        f"*{lifespan}*" if lifespan else "",
        f"**Works:** {work_count}",
        f"**Notable subjects:** {top_subjects}",
        f"**Best-known work:** {top_work}",
        f"\nhttps://openlibrary.org{author_key}",
    ]
    return "\n".join(l for l in lines if l)


async def books_isbn(isbn: str) -> str:
    """Get full details about a specific book by its ISBN.

    Args:
        isbn: The book's ISBN-10 or ISBN-13 (with or without dashes)
    """
    isbn_clean = isbn.replace("-", "").replace(" ", "")
    async with httpx.AsyncClient(timeout=12) as client:
        r = await client.get(f"{OL_API}/isbn/{isbn_clean}.json")
        if r.status_code == 404:
            return f"No book found for ISBN '{isbn}'. Make sure it's a valid ISBN-10 or ISBN-13."
        r.raise_for_status()
        data = r.json()

    title = data.get("title", "Unknown title")
    subtitle = data.get("subtitle", "")
    publishers = ", ".join(data.get("publishers", []))
    publish_date = data.get("publish_date", "?")
    pages = data.get("number_of_pages", "?")
    subjects = ", ".join(data.get("subjects", [])[:5])
    description = data.get("description", "")
    if isinstance(description, dict):
        description = description.get("value", "")

    return (
        f"# {title}" + (f": {subtitle}" if subtitle else "") + "\n\n"
        f"**Publisher:** {publishers} ({publish_date})\n"
        f"**Pages:** {pages}\n"
        f"**Subjects:** {subjects or 'N/A'}\n\n"
        f"{description[:400] + '...' if len(description) > 400 else description}\n\n"
        f"https://openlibrary.org/isbn/{isbn_clean}"
    )


async def books_trending() -> str:
    """Get currently trending books on Open Library."""
    async with httpx.AsyncClient(timeout=12) as client:
        r = await client.get(f"{OL_API}/trending/daily.json", params={"limit": 10})
        r.raise_for_status()
        data = r.json()

    works = data.get("works", [])
    if not works:
        return "No trending books found."

    results = ["**Trending Books Today**\n"]
    for w in works:
        title = w.get("title", "Untitled")
        authors = ", ".join(a.get("name", "") for a in w.get("authors", [])[:2])
        year = w.get("first_publish_year", "?")
        results.append(f"• **{title}** — {authors or 'Unknown'} ({year})")
    return "\n".join(results)


TOOLS = [books_search, books_author, books_isbn, books_trending]
