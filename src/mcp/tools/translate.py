"""
Translation MCP server.
No API key required — uses MyMemory free translation API (1000 words/day free tier).
"""

import httpx

MYMEMORY_API = "https://api.mymemory.translated.net/get"

LANGUAGES = {
    "af": "Afrikaans",
    "sq": "Albanian",
    "ar": "Arabic",
    "hy": "Armenian",
    "az": "Azerbaijani",
    "eu": "Basque",
    "be": "Belarusian",
    "bn": "Bengali",
    "bs": "Bosnian",
    "bg": "Bulgarian",
    "ca": "Catalan",
    "zh": "Chinese",
    "hr": "Croatian",
    "cs": "Czech",
    "da": "Danish",
    "nl": "Dutch",
    "en": "English",
    "eo": "Esperanto",
    "et": "Estonian",
    "fi": "Finnish",
    "fr": "French",
    "gl": "Galician",
    "ka": "Georgian",
    "de": "German",
    "el": "Greek",
    "gu": "Gujarati",
    "ht": "Haitian Creole",
    "he": "Hebrew",
    "hi": "Hindi",
    "hu": "Hungarian",
    "is": "Icelandic",
    "id": "Indonesian",
    "ga": "Irish",
    "it": "Italian",
    "ja": "Japanese",
    "kn": "Kannada",
    "kk": "Kazakh",
    "ko": "Korean",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "mk": "Macedonian",
    "ms": "Malay",
    "mt": "Maltese",
    "no": "Norwegian",
    "fa": "Persian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sr": "Serbian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "es": "Spanish",
    "sw": "Swahili",
    "sv": "Swedish",
    "tl": "Tagalog",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "cy": "Welsh",
}


async def translate_text(
    text: str, target_language: str, source_language: str = "auto"
) -> str:
    """Translate text into another language.

    Args:
        text: The text to translate (up to ~500 characters on free tier)
        target_language: Target language code (e.g. 'fr' for French, 'es' for Spanish, 'ja' for Japanese, 'de' for German)
        source_language: Source language code or 'auto' to detect automatically (default 'auto')
    """
    if source_language == "auto":
        lang_pair = f"en|{target_language}"
    else:
        lang_pair = f"{source_language}|{target_language}"

    async with httpx.AsyncClient(timeout=12) as client:
        r = await client.get(
            MYMEMORY_API,
            params={"q": text, "langpair": lang_pair},
        )
        r.raise_for_status()
        data = r.json()

    if data.get("responseStatus") != 200:
        return f"Translation failed: {data.get('responseDetails', 'Unknown error')}"

    translated = data.get("responseData", {}).get("translatedText", "")
    target_name = LANGUAGES.get(target_language, target_language)
    source_name = (
        LANGUAGES.get(source_language, source_language)
        if source_language != "auto"
        else "auto-detected"
    )

    return (
        f"**Original ({source_name}):**\n{text}\n\n"
        f"**Translation ({target_name}):**\n{translated}"
    )


async def translate_languages() -> str:
    """List all supported language codes for translation."""
    results = ["**Supported Languages**\n"]
    items = sorted(LANGUAGES.items(), key=lambda x: x[1])
    for code, name in items:
        results.append(f"  `{code}` — {name}")
    results.append(
        f"\n_{len(LANGUAGES)} languages supported. Use the code (e.g. 'fr') with translate_text._"
    )
    return "\n".join(results)


TOOLS = [translate_text, translate_languages]
