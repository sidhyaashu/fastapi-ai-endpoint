from pathlib import Path
from typing import Dict, Optional
from functools import lru_cache

PERSONAS_DIR = Path(__file__).parent.parent / "personas"

@lru_cache(maxsize=1)
def load_personas() -> Dict[str, str]:
    """Loads all persona files from the personas directory."""
    personas = {}
    if not PERSONAS_DIR.is_dir():
        return personas

    for file_path in PERSONAS_DIR.glob("*.md"):
        persona_name = file_path.stem
        with open(file_path, "r", encoding="utf-8") as f:
            personas[persona_name] = f.read()
    return personas

def get_persona_prompt(persona_name: str) -> Optional[str]:
    """Retrieves the system prompt for a given persona name."""
    personas = load_personas()
    return personas.get(persona_name)
