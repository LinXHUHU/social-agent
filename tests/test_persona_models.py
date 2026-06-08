from src.persona.models import Persona, Basic


def test_create_minimal_persona():
    p = Persona(persona_id="test_user", basic=Basic(name="测试"))
    assert p.persona_id == "test_user"
    assert p.basic.name == "测试"
    assert p.version == 1
    assert len(p.personality.traits) == 0
