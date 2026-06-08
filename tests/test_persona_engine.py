from src.persona.engine import PersonaEngine
from src.persona.models import Persona, Basic, Trait


def test_apply_updates_manual_not_overwritten(tmp_path, monkeypatch):
    monkeypatch.setattr("src.persona.storage.DATA_DIR", tmp_path)
    engine = PersonaEngine()
    p = engine.create("张三")
    # Add a manual trait (confidence=1.0)
    p.personality.traits = [Trait(trait="外向", confidence=1.0, evidence="观察")]
    from src.persona import storage
    storage.save(p)

    suggestions = [
        {"field": "personality.traits", "action": "add",
         "value": {"trait": "外向", "confidence": 0.3, "evidence": "AI推测"}}
    ]
    updated = engine.apply_updates(p.persona_id, suggestions)
    assert updated.personality.traits[0].confidence == 1.0  # unchanged


def test_apply_updates_adds_new_topic(tmp_path, monkeypatch):
    monkeypatch.setattr("src.persona.storage.DATA_DIR", tmp_path)
    engine = PersonaEngine()
    p = engine.create("李四")

    suggestions = [
        {"field": "strategies.topics_to_use", "action": "add", "value": "攀岩"}
    ]
    updated = engine.apply_updates(p.persona_id, suggestions)
    assert "攀岩" in updated.strategies.topics_to_use
