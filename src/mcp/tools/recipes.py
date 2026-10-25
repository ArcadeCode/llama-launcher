"""
Recipes MCP server.
No API key required — uses TheMealDB free API.
"""

import random

import httpx

MEAL_API = "https://www.themealdb.com/api/json/v1/1"


def _fmt_meal(meal: dict) -> str:
    name = meal.get("strMeal", "Unknown")
    category = meal.get("strCategory", "")
    area = meal.get("strArea", "")
    instructions = meal.get("strInstructions", "")[:600]
    youtube = meal.get("strYoutube", "")
    source = meal.get("strSource", "")

    # Extract ingredients (up to 20)
    ingredients = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}", "").strip()
        measure = meal.get(f"strMeasure{i}", "").strip()
        if ing:
            ingredients.append(f"  • {measure} {ing}".strip())

    lines = [
        f"# {name}",
        f"**Category:** {category}  |  **Cuisine:** {area}",
        "",
        "**Ingredients:**",
        *ingredients,
        "",
        "**Instructions:**",
        instructions + ("..." if len(meal.get("strInstructions", "")) > 600 else ""),
    ]
    if youtube:
        lines += ["", f"📺 Video: {youtube}"]
    if source:
        lines += [f"🔗 Source: {source}"]

    return "\n".join(lines)


async def recipes_search(query: str) -> str:
    """Search for recipes by meal name.

    Args:
        query: Meal name to search for (e.g. 'pasta', 'chicken tikka', 'chocolate cake')
    """
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{MEAL_API}/search.php", params={"s": query})
        r.raise_for_status()
        data = r.json()

    meals = data.get("meals") or []
    if not meals:
        return f"No recipes found for '{query}'. Try a different search term."

    if len(meals) == 1:
        return _fmt_meal(meals[0])

    results = [f"**Recipes matching '{query}'** ({len(meals)} found)\n"]
    for meal in meals[:8]:
        results.append(
            f"• **{meal.get('strMeal')}** — {meal.get('strCategory')} | {meal.get('strArea')}\n"
            f"  Ask for full recipe by name for details."
        )
    return "\n\n".join(results)


async def recipes_random() -> str:
    """Get a completely random recipe — great for meal inspiration."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{MEAL_API}/random.php")
        r.raise_for_status()
        data = r.json()

    meals = data.get("meals") or []
    if not meals:
        return "Could not fetch a random recipe right now."
    return _fmt_meal(meals[0])


async def recipes_by_category(category: str) -> str:
    """List meals in a given category.

    Args:
        category: Meal category (e.g. 'Seafood', 'Vegetarian', 'Dessert', 'Pasta', 'Chicken')
    """
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{MEAL_API}/filter.php", params={"c": category})
        r.raise_for_status()
        data = r.json()

    meals = data.get("meals") or []
    if not meals:
        cats_r = await httpx.AsyncClient(timeout=10).__aenter__()
        return f"No meals found in category '{category}'. Try: Seafood, Vegetarian, Dessert, Pasta, Chicken, Beef, Lamb."

    results = [f"**{category} recipes** ({len(meals)} total)\n"]
    for meal in meals[:15]:
        results.append(f"• {meal.get('strMeal')}")
    if len(meals) > 15:
        results.append(f"_(and {len(meals) - 15} more...)_")
    return "\n".join(results)


async def recipes_categories() -> str:
    """List all available meal categories."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{MEAL_API}/categories.php")
        r.raise_for_status()
        data = r.json()

    categories = data.get("categories") or []
    results = [f"**Available Recipe Categories** ({len(categories)} total)\n"]
    for cat in categories:
        name = cat.get("strCategory", "")
        desc = cat.get("strCategoryDescription", "")[:80]
        results.append(f"• **{name}** — {desc}...")
    return "\n\n".join(results)


TOOLS = [recipes_search, recipes_random, recipes_by_category, recipes_categories]
