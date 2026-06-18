"""i18n translation loader for seed data."""

import json
from pathlib import Path

_I18N_DIR = Path(__file__).parent / "i18n"


def load_translations(language: str) -> dict:
    """Load translations for the given language. Falls back to en.json."""
    path = _I18N_DIR / f"{language}.json"
    if not path.exists():
        path = _I18N_DIR / "en.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)
