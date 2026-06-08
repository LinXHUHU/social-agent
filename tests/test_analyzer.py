from src.analyzer.merger import merge_updates
from src.persona.models import Persona, Basic, Trait


def test_merge_adds_new_trait():
    p = Persona(persona_id="test", basic=Basic(name="测试"))
    suggestions = [
        {"field": "personality.traits", "action": "add",
         "value": Trait(trait="细心", confidence=0.7, evidence="发现格式错误").model_dump()}
    ]
    updated, conflicts = merge_updates(p, suggestions)
    assert len(updated.personality.traits) == 1
    assert updated.personality.traits[0].trait == "细心"
    assert len(conflicts) == 0


def test_merge_respects_manual_trait():
    p = Persona(persona_id="test", basic=Basic(name="测试"))
    p.personality.traits = [Trait(trait="细心", confidence=1.0, evidence="手动标注")]
    suggestions = [
        {"field": "personality.traits", "action": "add",
         "value": {"trait": "细心", "confidence": 0.3, "evidence": "AI推测"}}
    ]
    updated, conflicts = merge_updates(p, suggestions)
    assert updated.personality.traits[0].confidence == 1.0
    assert len(conflicts) == 1


def test_merge_adds_topic_string():
    p = Persona(persona_id="test", basic=Basic(name="测试"))
    suggestions = [
        {"field": "strategies.topics_to_use", "action": "add", "value": "攀岩"}
    ]
    updated, _ = merge_updates(p, suggestions)
    assert "攀岩" in updated.strategies.topics_to_use
