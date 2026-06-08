"""JSON file-based persona storage under ~/.social-agent/personas/."""
import json
import os
from pathlib import Path
from src.persona.models import Persona

DATA_DIR = Path.home() / ".social-agent" / "personas"


def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _path(persona_id: str) -> Path:
    return DATA_DIR / f"{persona_id}.json"


def save(persona: Persona):
    _ensure_dir()
    with open(_path(persona.persona_id), "w") as f:
        json.dump(persona.model_dump(), f, ensure_ascii=False, indent=2, default=str)


def load(persona_id: str) -> Persona | None:
    p = _path(persona_id)
    if not p.exists():
        return None
    with open(p) as f:
        data = json.load(f)
    return Persona(**data)


def delete(persona_id: str):
    p = _path(persona_id)
    if p.exists():
        p.unlink()


def list_all() -> list[str]:
    _ensure_dir()
    return [p.stem for p in DATA_DIR.glob("*.json")]
