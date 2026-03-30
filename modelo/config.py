"""
modelo/config.py — persistencia simple de configuración
(Solo maneja el tema actual)
"""
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")
CONFIG_PATH = os.path.normpath(CONFIG_PATH)

# 🔧 valor por defecto
_DEFAULTS = {
    "theme": "dark"
}


# ------------------------------------------------------------------
# Interno
# ------------------------------------------------------------------

def _load() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return dict(_DEFAULTS)


def _save(data: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ------------------------------------------------------------------
# API pública
# ------------------------------------------------------------------

def get_theme() -> str:
    return _load().get("theme", _DEFAULTS["theme"])


def set_theme(theme: str) -> None:
    data = _load()
    data["theme"] = theme
    _save(data)