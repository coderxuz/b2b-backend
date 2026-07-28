import json
from pathlib import Path


def load_translations() -> dict[str, dict[str, str]]:
    translations = {}
    locales_dir = Path(__file__).parent / "locales"
    for lang_file in locales_dir.glob("*.json"):
        lang = lang_file.stem
        with open(lang_file, "r", encoding="utf-8") as f:
            translations[lang] = json.load(f)
    return translations
