"""
Dictionary MCP server.
No API key required — uses the Free Dictionary API (dictionaryapi.dev).
"""

import httpx

DICT_API = "https://api.dictionaryapi.dev/api/v2/entries"


async def dictionary_define(word: str, language: str = "en") -> str:
    """Look up the definition of a word, including pronunciations, examples, and synonyms.

    Args:
        word: The word to look up (e.g. 'ephemeral', 'serendipity', 'ubiquitous')
        language: Language code (default 'en'). Supported: en, hi, es, fr, ja, ru, de, it, ko, ar, tr
    """
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{DICT_API}/{language}/{word.lower().strip()}")
        if r.status_code == 404:
            return f"No definition found for '{word}'. Check spelling or try another language."
        r.raise_for_status()
        data = r.json()

    if not data or not isinstance(data, list):
        return f"No results for '{word}'."

    entry = data[0]
    word_text = entry.get("word", word)
    phonetics = [p.get("text", "") for p in entry.get("phonetics", []) if p.get("text")]
    phonetic_str = f" /{phonetics[0]}/" if phonetics else ""

    lines = [f"# {word_text}{phonetic_str}\n"]

    for meaning in entry.get("meanings", []):
        part = meaning.get("partOfSpeech", "")
        lines.append(f"**_{part}_**")

        for i, defn in enumerate(meaning.get("definitions", [])[:3], 1):
            definition = defn.get("definition", "")
            example = defn.get("example", "")
            lines.append(f"{i}. {definition}")
            if example:
                lines.append(f'   _"{example}"_')

        synonyms = meaning.get("synonyms", [])[:5]
        antonyms = meaning.get("antonyms", [])[:5]
        if synonyms:
            lines.append(f"   **Synonyms:** {', '.join(synonyms)}")
        if antonyms:
            lines.append(f"   **Antonyms:** {', '.join(antonyms)}")
        lines.append("")

    return "\n".join(lines)


async def dictionary_synonyms(word: str) -> str:
    """Get synonyms and antonyms for a word.

    Args:
        word: The word to find synonyms/antonyms for
    """
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{DICT_API}/en/{word.lower().strip()}")
        if r.status_code == 404:
            return f"No results found for '{word}'."
        r.raise_for_status()
        data = r.json()

    if not data:
        return f"No results for '{word}'."

    all_synonyms: set[str] = set()
    all_antonyms: set[str] = set()

    for entry in data:
        for meaning in entry.get("meanings", []):
            all_synonyms.update(meaning.get("synonyms", []))
            all_antonyms.update(meaning.get("antonyms", []))
            for defn in meaning.get("definitions", []):
                all_synonyms.update(defn.get("synonyms", []))
                all_antonyms.update(defn.get("antonyms", []))

    lines = [f"**{word.title()}**\n"]
    if all_synonyms:
        lines.append(f"**Synonyms:** {', '.join(sorted(all_synonyms)[:15])}")
    else:
        lines.append("**Synonyms:** none found")
    if all_antonyms:
        lines.append(f"**Antonyms:** {', '.join(sorted(all_antonyms)[:15])}")
    else:
        lines.append("**Antonyms:** none found")

    return "\n".join(lines)


TOOLS = [dictionary_define, dictionary_synonyms]
