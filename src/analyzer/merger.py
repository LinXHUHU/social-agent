"""Conflict-aware merge of analyzer suggestions into persona."""
from src.persona.models import Persona, Trait


def _to_trait(value: dict) -> Trait:
    """Convert a dict to a Trait object."""
    return Trait(**value) if isinstance(value, dict) else value


def merge_updates(persona: Persona, suggestions: list[dict]) -> tuple:
    """Merge suggestions into a copy of persona with conflict detection.
    Returns (updated_persona, conflicts_resolved).
    Manual fields (confidence=1.0) are never overwritten."""
    conflicts = []
    updated = persona.model_copy(deep=True)

    for s in suggestions:
        field_path = s["field"]
        action = s.get("action", "add")
        value = s.get("value")

        if action != "add":
            continue

        parts = field_path.split(".")
        target = updated
        for part in parts[:-1]:
            target = getattr(target, part)
        attr_name = parts[-1]
        existing = getattr(target, attr_name)

        if isinstance(existing, list):
            if isinstance(value, dict) and "trait" in value:
                existing_trait = next(
                    (t for t in existing if hasattr(t, "trait") and t.trait == value["trait"]),
                    None
                )
                if existing_trait and existing_trait.confidence >= 1.0:
                    conflicts.append({
                        "field": field_path,
                        "reason": f"手动标注的'{value['trait']}'不被自动覆盖"
                    })
                    continue
                if existing_trait:
                    existing.remove(existing_trait)
                existing.append(_to_trait(value))
            elif isinstance(value, str) and value not in existing:
                existing.append(value)
            elif isinstance(value, list):
                for v in value:
                    if v not in existing:
                        existing.append(v)

    return updated, conflicts
