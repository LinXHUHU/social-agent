"""CoachEngine — 4-mode social coaching with knowledge injection."""
from src.persona.models import Persona
from src.coach import prompts
from src.knowledge.base import KnowledgeBase
from src.utils.deepseek import chat


class CoachEngine:
    def __init__(self, kb: KnowledgeBase | None = None):
        self.kb = kb

    def _inject_knowledge(self, persona: Persona) -> str:
        if not self.kb:
            return ""
        principles = self.kb.search(
            scene_labels=persona.basic.scene_tags,
            persona_traits=[t.trait for t in persona.personality.traits],
            limit=3,
        )
        if not principles:
            return ""
        lines = ["\n## 相关知识原则"]
        for p in principles:
            lines.append(f"- {p.principle}：{p.how_to_apply}")
        return "\n".join(lines)

    def advise_strategy(self, persona: Persona, scene: str = "") -> str:
        knowledge = self._inject_knowledge(persona)
        persona_json = prompts._render_persona(persona)
        user = f"## 人物画像\n{persona_json}\n{knowledge}\n\n## 当前场景\n{scene or '即将见面'}\n请给出策略分析。"
        return chat(system=prompts.STRATEGY_SYSTEM, user=user)

    def advise_analysis(self, persona: Persona, utterance: str,
                        context: list[str] | None = None) -> str:
        persona_json = prompts._render_persona(persona)
        ctx = "\n".join(f"- {line}" for line in (context or [])[-5:])
        user = f"## 人物画像\n{persona_json}\n\n## 最近对话\n{ctx or '(无)'}\n\n## 对方刚说的话\n{utterance}\n请分析。"
        return chat(system=prompts.ANALYSIS_SYSTEM, user=user, max_tokens=500)

    def advise_reply(self, persona: Persona, context: list[str],
                     style: str = "") -> str:
        persona_json = prompts._render_persona(persona)
        ctx = "\n".join(f"- {line}" for line in context[-10:])
        user = f"## 人物画像\n{persona_json}\n\n## 对话上下文\n{ctx}\n\n## 我的说话风格\n{style or persona.personality.communication_style or '自然随意'}\n请生成回复建议。"
        return chat(system=prompts.REPLY_SYSTEM, user=user, max_tokens=500)

    def advise_warmup(self, persona: Persona, context: list[str] | None = None) -> str:
        persona_json = prompts._render_persona(persona)
        ctx = "\n".join(f"- {line}" for line in (context or [])[-5:])
        user = f"## 人物画像\n{persona_json}\n\n## 最近对话\n{ctx or '(无)'}\n\n检测到冷场，请生成暖场话题。"
        return chat(system=prompts.WARMUP_SYSTEM, user=user, max_tokens=600)
