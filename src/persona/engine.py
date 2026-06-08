"""PersonaEngine — CRUD + conflict-aware persona updates."""
from datetime import datetime
from src.persona.models import Persona, Basic
from src.persona import storage


class PersonaEngine:
    def create(self, name: str, initial: dict | None = None) -> Persona:
        p = Persona(persona_id=_slugify(name), basic=Basic(name=name))
        if initial:
            p = p.model_copy(update=initial)
        storage.save(p)
        return p

    def get(self, persona_id: str) -> Persona:
        p = storage.load(persona_id)
        if p is None:
            raise KeyError(f"未找到画像: {persona_id}")
        return p

    def list_all(self) -> list[Persona]:
        return [storage.load(pid) for pid in storage.list_all()]

    def update(self, persona_id: str, updates: dict) -> Persona:
        p = self.get(persona_id)
        p = p.model_copy(update=updates)
        p.version += 1
        p.updated_at = datetime.now().isoformat()
        storage.save(p)
        return p

    def apply_updates(self, persona_id: str, suggestions: list[dict]) -> Persona:
        """Apply analyzer suggestions with conflict detection.
        Manual (confidence=1.0) fields are never overwritten."""
        p = self.get(persona_id)
        for s in suggestions:
            if s["action"] != "add":
                continue
            p = _merge_field(p, s["field"], s["value"])
        p.version += 1
        p.updated_at = datetime.now().isoformat()
        storage.save(p)
        return p

    def delete(self, persona_id: str):
        storage.delete(persona_id)


def _slugify(name: str) -> str:
    import re
    slug = name.strip().lower().replace(" ", "_")
    slug = re.sub(r"[^\w]", "", slug)
    return slug or "persona"


def _merge_field(persona: Persona, field: str, value) -> Persona:
    """Add value to a list field, deduplicating. Never overwrites confidence=1.0."""
    parts = field.split(".")
    obj = persona
    for part in parts[:-1]:
        obj = getattr(obj, part)
    list_field = parts[-1]
    existing = getattr(obj, list_field, [])

    if isinstance(value, dict):
        # For traits, check if same trait name exists and merge by confidence
        if "trait" in value:
            for i, item in enumerate(existing):
                if hasattr(item, "trait") and item.trait == value["trait"]:
                    if item.confidence >= 1.0:
                        return persona  # manual override, don't touch
                    # update lower confidence entry
                    existing[i] = item.model_copy(update=value)
                    return persona
        if existing:
            existing.append(type(existing[0])(**value))
        elif field.startswith("personality.traits"):
            from src.persona.models import Trait
            existing.append(Trait(**value))
        else:
            existing.append(value)
    elif isinstance(value, str):
        if value not in existing:
            existing.append(value)

    setattr(obj, list_field, existing)
    return persona
