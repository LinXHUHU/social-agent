import os
import pytest
from src.coach.engine import CoachEngine
from src.persona.models import Persona, Basic


@pytest.mark.skipif(not os.environ.get("DEEPSEEK_API_KEY"), reason="需要 API key")
def test_advise_strategy():
    engine = CoachEngine()
    p = Persona(persona_id="test", basic=Basic(name="测试", relationship="同事",
        scene_tags=["职场"]))
    p.goals.my_goal = "建立信任"
    result = engine.advise_strategy(p, "公司茶水间偶遇")
    assert len(result) > 0
    print(result)
