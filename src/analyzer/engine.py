"""Analyzer — conversation analysis + persona update suggestions."""
from src.persona.models import Persona
from src.utils.deepseek import chat

ANALYZE_SYSTEM = """你是一位专业的社交对话分析师。你需要分析一段对话，并给出：
1. 对话分析报告
2. 画像更新建议

## 分析要求
- 情绪曲线：标注每轮对话的情绪变化和触发点
- 关键转折：气氛升温点和踩雷点
- 我的表现：优点和改进空间
- 关系信号：当前状态、趋势、下一步建议

## 画像更新要求
- 发现新的性格特征、喜好、禁忌时提出添加建议
- 每条更新需要附带置信度(0-1)和证据（引用对话原文）
- 如果当前推断的证据不足，标注"confidence_warning"

请严格按照JSON格式返回，不要有其他输出。
{
  "report": {"summary": "...", "emotion_curve": [...], ...},
  "updates": [...],
  "confidence_warnings": [...]
}
"""


class Analyzer:
    def analyze(self, conversation: str, persona: Persona | None = None,
                scene: dict | None = None) -> dict:
        persona_info = "无"
        if persona:
            import json
            persona_info = json.dumps({
                "name": persona.basic.name,
                "relationship": persona.basic.relationship,
                "known_traits": [t.trait for t in persona.personality.traits],
                "current_goals": persona.goals.my_goal,
            }, ensure_ascii=False)

        scene_info = f"场景: {scene}" if scene else ""
        user = f"## 人物信息\n{persona_info}\n{scene_info}\n\n## 对话内容\n{conversation}"
        result = chat(system=ANALYZE_SYSTEM, user=user, max_tokens=2000)
        import json as _json
        return _json.loads(result)

    def suggest_updates(self, analysis_result: dict) -> list[dict]:
        return analysis_result.get("updates", [])
