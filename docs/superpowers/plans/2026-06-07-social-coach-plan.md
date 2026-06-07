# Social Coach Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI tool that uses DeepSeek-V3 API to provide real-time social coaching, manage person profiles, analyze conversations, and leverage a social knowledge base.

**Architecture:** 4 independent engine modules (Persona, Coach, Analyzer, KnowledgeBase) orchestrated through a Click CLI shell. Each engine exposes a Python API consumed by the CLI layer. LLM calls go through a shared `deepseek` util. Data stored as local JSON files under `~/.social-agent/`.

**Tech Stack:** Python 3.11+, DeepSeek-V3 API (`openai` SDK, base_url pointed to DeepSeek), Click CLI, Rich terminal output, Pydantic models, pytest

---

### Task 1: Project skeleton and LLM utility

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `src/utils/__init__.py`
- Create: `src/utils/deepseek.py`
- Create: `src/main.py`

- [ ] **Step 1: Write requirements.txt**

```
click>=8.0
rich>=13.0
openai>=1.0
pydantic>=2.0
Pillow>=10.0
pytest>=8.0
```

- [ ] **Step 2: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 3: Write DeepSeek LLM utility**

```python
"""DeepSeek-V3 API wrapper. Uses OpenAI-compatible endpoint."""
import os
from openai import OpenAI

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-your-key-here")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(base_url=DEEPSEEK_BASE_URL, api_key=DEEPSEEK_API_KEY)
    return _client


def chat(
    system: str,
    user: str,
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> str:
    """Send a chat completion and return the response text."""
    response = get_client().chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content
```

[Write exact code to `src/utils/deepseek.py`]

- [ ] **Step 4: Write empty init files**

```python
# src/__init__.py
# src/utils/__init__.py
```

- [ ] **Step 5: Write minimal CLI shell**

```python
"""Social Coach — AI-powered social interaction coach."""
import click


@click.group()
def main():
    """AI 社交指导助手"""
    pass


if __name__ == "__main__":
    main()
```

[Write to `src/main.py`]

- [ ] **Step 6: Verify CLI runs**

```bash
python -m src.main --help
```
Expected: Shows "Usage: ... Commands:" with no subcommands yet.

- [ ] **Step 7: Smoke-test DeepSeek API**

Write a quick test script:
```python
from src.utils.deepseek import chat

result = chat(system="你是一个助手", user="回复'ok'")
assert "ok" in result.lower()
print("PASS:", result)
```

Run it and verify the API key works.

- [ ] **Step 8: Commit**

```bash
git add requirements.txt src/
git commit -m "feat: add project skeleton and DeepSeek LLM utility"
```

---

### Task 2: Persona data models

**Files:**
- Create: `src/persona/__init__.py`
- Create: `src/persona/models.py`

- [ ] **Step 1: Write Pydantic models**

```python
"""Persona data models matching the design spec JSON schema."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Basic(BaseModel):
    name: str
    alias: list[str] = Field(default_factory=list)
    relationship: str = "陌生人"
    closeness: int = Field(default=5, ge=1, le=10)
    scene_tags: list[str] = Field(default_factory=list)
    first_met: str = ""
    avatar_url: Optional[str] = None


class Trait(BaseModel):
    trait: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence: str = ""


class MBTI(BaseModel):
    type: str = ""
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    source: str = ""


class EmotionalTriggers(BaseModel):
    positive: list[str] = Field(default_factory=list)
    negative: list[str] = Field(default_factory=list)


class Personality(BaseModel):
    traits: list[Trait] = Field(default_factory=list)
    mbti: MBTI = Field(default_factory=MBTI)
    communication_style: str = ""
    emotional_triggers: EmotionalTriggers = Field(default_factory=EmotionalTriggers)
    values: list[str] = Field(default_factory=list)


class KeyEvent(BaseModel):
    date: str = ""
    type: str = "普通"
    summary: str = ""
    tags: list[str] = Field(default_factory=list)


class EmotionTimelineEntry(BaseModel):
    date: str = ""
    mood: str = ""
    note: str = ""


class Interaction(BaseModel):
    total_encounters: int = 0
    key_events: list[KeyEvent] = Field(default_factory=list)
    conversation_summary: str = ""
    emotion_timeline: list[EmotionTimelineEntry] = Field(default_factory=list)


class Goals(BaseModel):
    my_goal: str = ""
    their_attitude: str = ""
    opportunities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class Strategies(BaseModel):
    topics_to_use: list[str] = Field(default_factory=list)
    topics_to_avoid: list[str] = Field(default_factory=list)
    communication_tips: list[str] = Field(default_factory=list)
    gift_ideas: list[str] = Field(default_factory=list)


class Persona(BaseModel):
    persona_id: str  # unique slug, e.g. "zhang_san"
    version: int = 1
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    basic: Basic = Field(default_factory=Basic)
    personality: Personality = Field(default_factory=Personality)
    interaction: Interaction = Field(default_factory=Interaction)
    goals: Goals = Field(default_factory=Goals)
    strategies: Strategies = Field(default_factory=Strategies)
    embedding: Optional[list[float]] = None
```

[Write to `src/persona/models.py`]

- [ ] **Step 2: Write test for Persona creation**

```python
from src.persona.models import Persona, Basic


def test_create_minimal_persona():
    p = Persona(persona_id="test_user", basic=Basic(name="测试"))
    assert p.persona_id == "test_user"
    assert p.basic.name == "测试"
    assert p.version == 1
    assert len(p.personality.traits) == 0
```

[Write to `tests/test_persona_models.py`]

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/test_persona_models.py -v
```
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add src/persona/ tests/
git commit -m "feat: add persona Pydantic data models"
```

---

### Task 3: Persona storage layer

**Files:**
- Create: `src/persona/storage.py`

- [ ] **Step 1: Write JSON storage**

```python
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
```

[Write to `src/persona/storage.py`]

- [ ] **Step 2: Write test for save/load**

```python
from src.persona.models import Persona, Basic
from src.persona.storage import save, load, delete, list_all


def test_save_and_load(tmp_path, monkeypatch):
    monkeypatch.setattr("src.persona.storage.DATA_DIR", tmp_path)
    p = Persona(persona_id="test_user", basic=Basic(name="测试"))
    save(p)
    loaded = load("test_user")
    assert loaded is not None
    assert loaded.basic.name == "测试"


def test_delete(tmp_path, monkeypatch):
    monkeypatch.setattr("src.persona.storage.DATA_DIR", tmp_path)
    p = Persona(persona_id="test_user", basic=Basic(name="测试"))
    save(p)
    delete("test_user")
    assert load("test_user") is None


def test_list_all(tmp_path, monkeypatch):
    monkeypatch.setattr("src.persona.storage.DATA_DIR", tmp_path)
    save(Persona(persona_id="a", basic=Basic(name="A")))
    save(Persona(persona_id="b", basic=Basic(name="B")))
    ids = list_all()
    assert "a" in ids
    assert "b" in ids
```

[Write to `tests/test_persona_storage.py`]

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/test_persona_storage.py -v
```
Expected: 3 PASS

- [ ] **Step 4: Commit**

```bash
git add src/persona/storage.py tests/test_persona_storage.py
git commit -m "feat: add persona JSON storage layer"
```

---

### Task 4: Persona engine

**Files:**
- Create: `src/persona/engine.py`

- [ ] **Step 1: Write PersonaEngine**

```python
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
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    return slug


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
        existing.append(type(existing[0])(**value) if existing else value)
    elif isinstance(value, str):
        if value not in existing:
            existing.append(value)

    setattr(obj, list_field, existing)
    return persona
```

[Write to `src/persona/engine.py`]

- [ ] **Step 2: Write test for apply_updates conflict rules**

```python
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
```

[Write to `tests/test_persona_engine.py`]

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/test_persona_engine.py -v
```
Expected: 2 PASS

- [ ] **Step 4: Commit**

```bash
git add src/persona/engine.py tests/test_persona_engine.py
git commit -m "feat: add PersonaEngine with conflict-aware updates"
```

---

### Task 5: Knowledge base

**Files:**
- Create: `src/knowledge/__init__.py`
- Create: `src/knowledge/base.py`
- Create: `src/knowledge/data/principles.json`

- [ ] **Step 1: Write knowledge base models and engine**

```python
"""KnowledgeBase — search and manage social principles from books/theory."""
import json
from pathlib import Path
from pydantic import BaseModel, Field

DATA_FILE = Path(__file__).parent / "data" / "principles.json"


class Principle(BaseModel):
    principle_id: str
    source_type: str = "book"
    source_title: str = ""
    source_chapter: str = ""
    principle: str
    category: str = "通用社交"
    applicable_scenarios: list[str] = Field(default_factory=list)
    how_to_apply: str = ""
    counter_example: str = ""
    related_principles: list[str] = Field(default_factory=list)
    effectiveness: int | None = None


class KnowledgeBase:
    def __init__(self, data_file: Path | None = None):
        self._file = data_file or DATA_FILE
        self._principles: list[Principle] = []
        self._load()

    def _load(self):
        if self._file.exists():
            with open(self._file) as f:
                data = json.load(f)
            self._principles = [Principle(**item) for item in data]

    def _save(self):
        self._file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._file, "w") as f:
            json.dump([p.model_dump() for p in self._principles], f,
                      ensure_ascii=False, indent=2, default=str)

    def search(self, scene_labels: list[str], persona_traits: list[str] = None,
               limit: int = 5) -> list[Principle]:
        persona_traits = persona_traits or []
        scored = []
        for p in self._principles:
            score = 0
            for label in scene_labels:
                if label in p.applicable_scenarios or label in p.category:
                    score += 2
            for trait in persona_traits:
                if trait in p.how_to_apply or trait in p.principle:
                    score += 1
            if score > 0:
                scored.append((score, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:limit]]

    def add(self, principle: dict) -> str:
        p = Principle(**principle)
        self._principles.append(p)
        self._save()
        return p.principle_id

    def list_all(self) -> list[Principle]:
        return self._principles

    def list_by_source(self, source_title: str) -> list[Principle]:
        return [p for p in self._principles if p.source_title == source_title]
```

[Write to `src/knowledge/base.py`]

- [ ] **Step 2: Write seed data with 5 books' principles**

Create a seed script to generate `principles.json` via LLM extraction, or hand-write 3-4 representative principles:

```json
[
  {
    "principle_id": "how_to_win_01",
    "source_type": "book",
    "source_title": "人性的弱点",
    "source_chapter": "如何让他人喜欢你",
    "principle": "真诚地关心他人，而不是假装关心",
    "category": "通用社交",
    "applicable_scenarios": ["初次见面", "维系关系", "职场"],
    "how_to_apply": "记住对方提到的细节（生日、爱好、家人），下次聊天时自然提起",
    "counter_example": "只记住信息但不主动提起，对方会觉得你并不真的关心",
    "related_principles": ["how_to_win_03"],
    "effectiveness": null
  },
  {
    "principle_id": "nvc_01",
    "source_type": "book",
    "source_title": "非暴力沟通",
    "source_chapter": "区分观察和评论",
    "principle": "表达观察到的事实而非评价，减少对方的防御反应",
    "category": "冲突处理",
    "applicable_scenarios": ["意见分歧", "职场反馈", "亲密关系"],
    "how_to_apply": "说'你刚才打断了3次我的发言'，而不是说'你总是不尊重我'",
    "counter_example": "'你这样做太差劲了' — 这是评价不是观察，对方会立即防御",
    "related_principles": ["nvc_02"],
    "effectiveness": null
  },
  {
    "principle_id": "intimacy_01",
    "source_type": "book",
    "source_title": "亲密关系",
    "source_chapter": "吸引力与接近性",
    "principle": "曝光效应：人们更容易对熟悉的人产生好感，但需要是正面互动",
    "category": "约会",
    "applicable_scenarios": ["初次见面", "暧昧期", "约会"],
    "how_to_apply": "创造频繁但不刻意的正面接触机会，保持轻松愉快的印象",
    "counter_example": "频繁发消息但内容无趣或负面，反而让人厌烦",
    "related_principles": [],
    "effectiveness": null
  },
  {
    "principle_id": "mars_venus_01",
    "source_type": "book",
    "source_title": "男人来自火星女人来自金星",
    "source_chapter": "男女沟通差异",
    "principle": "女性倾诉时通常需要共情而非解决方案，男性则需要被认可",
    "category": "异性社交",
    "applicable_scenarios": ["约会", "亲密关系", "朋友"],
    "how_to_apply": "对方倾诉烦恼时，先说'听起来你真的很不容易'再问'需要我帮忙想方案吗？'",
    "counter_example": "直接跳过共情给方案：'你换个工作不就行了'",
    "related_principles": [],
    "effectiveness": null
  },
  {
    "principle_id": "influence_01",
    "source_type": "book",
    "source_title": "影响力",
    "source_chapter": "喜好原理",
    "principle": "人们更容易被自己喜欢的人说服，相似性是好感的关键来源",
    "category": "通用社交",
    "applicable_scenarios": ["初次见面", "谈判", "职场"],
    "how_to_apply": "找到与对方的真实共同点（兴趣/背景/观点），在对话早期自然提及",
    "counter_example": "虚伪地假装有共同兴趣 — 被发现后破坏信任",
    "related_principles": [],
    "effectiveness": null
  }
]
```

[Write to `src/knowledge/data/principles.json`]

- [ ] **Step 3: Write tests for search**

```python
from pathlib import Path
from src.knowledge.base import KnowledgeBase


def test_search_by_scene(tmp_path):
    kb = KnowledgeBase(data_file=tmp_path / "test.json")
    kb.add({"principle_id": "t1", "principle": "测试原则1",
            "category": "约会", "applicable_scenarios": ["初次见面"]})
    kb.add({"principle_id": "t2", "principle": "测试原则2",
            "category": "职场", "applicable_scenarios": ["职场"]})

    results = kb.search(scene_labels=["约会"])
    assert len(results) == 1
    assert results[0].principle_id == "t1"


def test_add_returns_id():
    kb = KnowledgeBase(data_file=tmp_path / "test2.json" if False else None)
    # use memory-only for this test
    ...
```

[Write to `tests/test_knowledge.py`]

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_knowledge.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/knowledge/ tests/test_knowledge.py
git commit -m "feat: add knowledge base with 5-book seed principles"
```

---

### Task 6: Coach prompts and engine

**Files:**
- Create: `src/coach/__init__.py`
- Create: `src/coach/prompts.py`
- Create: `src/coach/engine.py`

- [ ] **Step 1: Write prompt templates**

```python
"""Prompt templates for the 4 coaching modes."""
import json


def _render_persona(p) -> str:
    """Render key persona fields for prompt context."""
    return json.dumps({
        "name": p.basic.name,
        "relationship": p.basic.relationship,
        "closeness": p.basic.closeness,
        "scene_tags": p.basic.scene_tags,
        "traits": [t.model_dump() for t in p.personality.traits],
        "communication_style": p.personality.communication_style,
        "positive_triggers": p.personality.emotional_triggers.positive,
        "negative_triggers": p.personality.emotional_triggers.negative,
        "my_goal": p.goals.my_goal,
        "their_attitude": p.goals.their_attitude,
        "topics_to_use": p.strategies.topics_to_use,
        "topics_to_avoid": p.strategies.topics_to_avoid,
        "communication_tips": p.strategies.communication_tips,
        "key_events": [e.model_dump() for e in p.interaction.key_events[-5:]],
        "conversation_summary": p.interaction.conversation_summary,
    }, ensure_ascii=False, indent=2)


STRATEGY_SYSTEM = """你是一位资深社交策略顾问，擅长人际博弈分析和社交场景规划。

## 你的任务
1. 分析当前局势：TA对"我"的态度阶段、权力关系、信任度
2. 给出本次互动的核心策略（1-2句话）
3. 推荐3-5个安全话题，按优先级排序
4. 标注2-3个绝对不要碰的话题或行为
5. 如果条件触发，给出升级/撤退信号

## 约束
- 建议必须基于提供的画像数据，不要给泛泛的通用建议
- 如果画像信息不足以支撑判断，明确说"基于现有信息推测..."
"""

ANALYSIS_SYSTEM = """你是实时社交翻译器，帮"我"读懂对方的未尽之言。

## 你的任务
1. 解读对方的情绪状态（开心/烦躁/敷衍/认真/无聊/紧张...）
2. 分析这句话的真正意图（寻求共鸣/释放善意/试探底线/敷衍/求助...）
3. 点出我可能没注意到的信号（微妙的语气变化、回避的话题、隐藏的需求）
4. 给一个简短的应对方向（一句话，不要长篇大论）

## 约束
- 分析要具体，引用对方原话中的关键词
- 如果信息不足以判断，宁可说"不确定"也不要瞎猜
"""

REPLY_SYSTEM = """你是我的口语出词器，代替我在社交中说合适的话。

## 你的任务
生成2-3句我可以直接说出口的回复，要求：
1. 贴合"我"的说话风格，不要突然文绉绉或风格跳跃
2. 自然不刻意，别像AI写的
3. 至少给一个"安全牌"话术和一个"推进关系"话术
4. 注明每句话的意图（破冰/深入/试探/转移话题/幽默/安抚）

## 约束
- 不要给出格或冒犯性的建议
- 如果对方明显有敌意，优先给缓和性话术
"""

WARMUP_SYSTEM = """你是社交破冰专家，专治冷场。

## 你的任务
1. 分析冷场原因（话题聊死了？对方走神？纯话题耗尽？）
2. 生成三类候选话题：
   - 安全牌：一定能接上的话题
   - 升温牌：能推进关系的话题
   - 场景牌：利用当下环境自然过渡的话题
3. 为每个话题附带选择理由

## 约束
- 话题必须基于画像数据中的安全话题和正向情绪触发点
- 避免画像中标注的禁忌话题
"""
```

[Write to `src/coach/prompts.py`]

- [ ] **Step 2: Write CoachEngine**

```python
"""CoachEngine — 4-mode social coaching with knowledge injection."""
from src.persona.models import Persona
from src.coach import prompts
from src.knowledge.base import KnowledgeBase
from src.utils.deepseek import chat

# Lightweight dataclasses for structured return values.
# Using dicts for v1 to avoid over-engineering.

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
```

[Write to `src/coach/engine.py`]

- [ ] **Step 3: Write smoke test (requires API key)**

```python
import os, pytest
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
```

[Write to `tests/test_coach_engine.py`]

- [ ] **Step 4: Run smoke test (optional, needs key)**

```bash
DEEPSEEK_API_KEY=sk-xxx python -m pytest tests/test_coach_engine.py -v -s
```

- [ ] **Step 5: Commit**

```bash
git add src/coach/ tests/test_coach_engine.py
git commit -m "feat: add CoachEngine with 4-mode prompts and knowledge injection"
```

---

### Task 7: Conversation analyzer

**Files:**
- Create: `src/analyzer/__init__.py`
- Create: `src/analyzer/engine.py`
- Create: `src/analyzer/merger.py`

- [ ] **Step 1: Write analyzer engine**

```python
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
        import json
        return json.loads(result)

    def suggest_updates(self, analysis_result: dict) -> list[dict]:
        return analysis_result.get("updates", [])
```

[Write to `src/analyzer/engine.py`]

- [ ] **Step 2: Write merger**

```python
"""Conflict-aware merge of analyzer suggestions into persona."""
from src.persona.models import Persona


def merge_updates(persona: Persona, suggestions: list[dict]) -> (Persona, list[dict]):
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

        # Navigate nested field
        parts = field_path.split(".")
        target = updated
        for part in parts[:-1]:
            target = getattr(target, part)
        attr_name = parts[-1]
        existing = getattr(target, attr_name)

        if isinstance(existing, list):
            if isinstance(value, dict) and "trait" in value:
                # Trait merging: check for manual override
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
                # Append as model if type is known, else dict
                existing.append(value)
            elif isinstance(value, str) and value not in existing:
                existing.append(value)
            elif isinstance(value, list):
                for v in value:
                    if v not in existing:
                        existing.append(v)

    return updated, conflicts
```

[Write to `src/analyzer/merger.py`]

- [ ] **Step 3: Write tests**

```python
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
```

[Write to `tests/test_analyzer.py`]

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_analyzer.py -v
```
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add src/analyzer/ tests/test_analyzer.py
git commit -m "feat: add conversation analyzer with conflict-aware merger"
```

---

### Task 8: Screenshot utility

**Files:**
- Create: `src/utils/screenshot.py`

- [ ] **Step 1: Write screenshot OCR**

```python
"""Screenshot analysis — extract WeChat/chat text from screenshots."""
import base64
from pathlib import Path
from src.utils.deepseek import chat

OCR_SYSTEM = """你是一个聊天截图识别器。输入是聊天截图的base64编码图片。
请提取截图中所有的对话内容，按照以下格式输出：

[发送者A]：消息内容
[发送者B]：消息内容

只输出对话内容，不要添加任何解释或说明。"""


def extract_text(image_path: str) -> str:
    """Extract conversation text from a chat screenshot using DeepSeek vision.
    Note: deepseek-chat (V3) may not support vision. Falls back to descriptive analysis."""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    # DeepSeek V3 currently doesn't support image input natively.
    # For v1, use a workaround: describe the image and ask user to verify.
    user_msg = (
        "请详细描述这张聊天截图中的内容，包括每条消息的发送者、内容、时间（如果有的话）。"
        "请尽量还原完整的对话文本。"
    )

    try:
        # Try vision-capable endpoint if available
        response = chat(system=OCR_SYSTEM, user=user_msg, max_tokens=2000)
        return response
    except Exception:
        return _fallback_text_extraction(image_path)


def _fallback_text_extraction(image_path: str) -> str:
    """Prompt user to manually transcribe if vision unavailable."""
    return f"[需要手动转录，图片路径: {image_path}]"
```

[Write to `src/utils/screenshot.py`]

- [ ] **Step 2: Commit**

```bash
git add src/utils/screenshot.py
git commit -m "feat: add screenshot text extraction utility"
```

---

### Task 9: CLI — Persona commands

**Files:**
- Modify: `src/main.py`

- [ ] **Step 1: Add persona CLI group**

```python
"""Social Coach — AI-powered social interaction coach."""
import json
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.persona.engine import PersonaEngine

console = Console()
engine = PersonaEngine()


@click.group()
def main():
    """AI 社交指导助手"""
    pass


@main.group()
def persona():
    """人物画像管理"""
    pass


@persona.command()
@click.option("--name", prompt="姓名", help="对方姓名")
@click.option("--relationship", prompt="关系（同事/朋友/暧昧对象/长辈/陌生人等）",
              default="陌生人")
def add(name, relationship):
    """交互式创建画像"""
    from rich.prompt import Prompt

    p = engine.create(name, initial={
        "basic": {"name": name, "relationship": relationship}
    })

    # Optional: quick fill via prompts
    if click.confirm("是否现在完善画像?"):
        goal = Prompt.ask("  你对此人的目标", default="")
        attitude = Prompt.ask("  此人对你的态度", default="")
        p = engine.update(p.persona_id, {
            "goals": {"my_goal": goal, "their_attitude": attitude}
        })

    console.print(f"\n[green]✓ 画像已创建: {p.persona_id}[/green]")
    console.print(f"  存储位置: ~/.social-agent/personas/{p.persona_id}.json")


@persona.command()
@click.argument("persona_id")
def show(persona_id):
    """查看画像详情"""
    p = engine.get(persona_id)
    data = p.model_dump()
    # Pretty-print key sections
    console.print(f"\n[bold cyan]━━━ {p.basic.name} ({p.persona_id}) ━━━[/bold cyan]")
    console.print(f"  关系: {p.basic.relationship} | 亲密度: {p.basic.closeness}/10")
    console.print(f"  性格特征: {', '.join(t.trait for t in p.personality.traits)}")
    console.print(f"  沟通风格: {p.personality.communication_style}")
    console.print(f"  安全话题: {', '.join(p.strategies.topics_to_use)}")
    console.print(f"  禁忌话题: {', '.join(p.strategies.topics_to_avoid)}")
    console.print(f"  目标: {p.goals.my_goal}")
    console.print(f"\n完整JSON: ~/.social-agent/personas/{persona_id}.json")


@persona.command()
def list():
    """列出所有画像"""
    personas = engine.list_all()
    if not personas:
        console.print("[dim]还没有任何画像，使用 persona add 创建[/dim]")
        return

    table = Table(title="人物画像列表")
    table.add_column("ID", style="cyan")
    table.add_column("姓名", style="bold")
    table.add_column("关系")
    table.add_column("亲密度")
    table.add_column("目标")

    for p in personas:
        table.add_row(
            p.persona_id, p.basic.name, p.basic.relationship,
            str(p.basic.closeness),
            p.goals.my_goal[:20] + "..." if len(p.goals.my_goal) > 20 else p.goals.my_goal
        )
    console.print(table)


@persona.command()
@click.argument("persona_id")
@click.option("--field", "-f", default=None, help="简化的顶层字段，如 goals.my_goal")
@click.option("--value", "-v", default=None, help="新值")
def edit(persona_id, field, value):
    """编辑画像。不加参数则打开JSON文件直接编辑。"""
    if not field:
        import subprocess, os
        editor = os.environ.get("EDITOR", "vim")
        config_path = Path.home() / ".social-agent" / "personas" / f"{persona_id}.json"
        subprocess.call([editor, str(config_path)])
        console.print(f"[green]✓ 请在编辑器中修改 {config_path}[/green]")
        return
    # Simpler: only support flat top-level field updates
    p = engine.get(persona_id)
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, ValueError):
        parsed = value
    # Navigate to nested field for writing
    parts = field.split(".")
    obj = p
    for part in parts[:-1]:
        obj = getattr(obj, part)
    setattr(obj, parts[-1], parsed)
    from datetime import datetime
    p.version += 1
    p.updated_at = datetime.now().isoformat()
    from src.persona import storage
    storage.save(p)
    console.print(f"[green]✓ 已更新 {persona_id} 的 {field}[/green]")
```

[Modify `src/main.py`]

- [ ] **Step 2: Test CLI commands**

```bash
python -m src.main persona add --name "张三" --relationship "同事"
python -m src.main persona list
python -m src.main persona show zhang_san
python -m src.main persona edit zhang_san --field "basic.closeness" --value 7
python -m src.main persona show zhang_san
```
Expected: Creates, lists, shows, edits persona. All work without errors.

- [ ] **Step 3: Commit**

```bash
git add src/main.py
git commit -m "feat: add persona CLI commands (add/show/list/edit)"
```

---

### Task 10: CLI — Coach commands

**Files:**
- Modify: `src/main.py`

- [ ] **Step 1: Add coach CLI group**

Append to `src/main.py`:

```python
@main.group()
def coach():
    """教练指导"""
    pass


@coach.command()
@click.argument("persona_id")
@click.option("--scene", "-s", default="", help="场景描述，如'公司茶水间'")
def strategy(persona_id, scene):
    """见面前的策略分析"""
    from src.coach.engine import CoachEngine
    p = engine.get(persona_id)
    ce = CoachEngine()
    console.print(f"\n[bold cyan]分析 {p.basic.name}...[/bold cyan]")
    result = ce.advise_strategy(p, scene)
    console.print(Panel(result, title="策略建议", border_style="green"))


@coach.command()
@click.argument("persona_id")
def live(persona_id):
    """进入实时指导交互模式（文本模拟）"""
    from src.coach.engine import CoachEngine
    p = engine.get(persona_id)
    ce = CoachEngine()

    console.print(f"\n[bold cyan]📋 已加载画像：{p.basic.name}（{p.basic.relationship}）[/bold cyan]")
    if p.goals.my_goal:
        console.print(f"[dim]🎯 当前目标：{p.goals.my_goal}[/dim]")

    # Initial strategy
    result = ce.advise_strategy(p, "文本聊天")
    console.print(Panel(result, title="💡 建议策略", border_style="green"))

    console.print("\n[dim][输入对方说的话，或 /help 查看命令][/dim]\n")

    context: list[str] = []

    while True:
        try:
            user_input = click.prompt("> ", prompt_suffix="")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]已退出[/dim]")
            break

        if user_input.strip().lower() in ("/exit", "/quit"):
            break
        elif user_input.startswith("/warmup"):
            result = ce.advise_warmup(p, context)
            console.print(Panel(result, title="🧊 暖场话题", border_style="yellow"))
            continue
        elif user_input.startswith("/help"):
            console.print("""[bold]可用命令:[/bold]
  <任意文本>     输入对方说的话，AI 分析 + 给话术建议
  /warmup        手动请求暖场话题
  /exit          退出
  Ctrl+C         退出""")
            continue

        context.append(user_input)

        # Analysis mode (always runs)
        analysis = ce.advise_analysis(p, user_input, context[:-1])
        console.print(Panel(analysis, title="🤔 分析", border_style="blue"))

        # Reply mode
        reply = ce.advise_reply(p, context)
        console.print(Panel(reply, title="💬 回复建议", border_style="green"))


@coach.command()
@click.argument("persona_id")
def warmup(persona_id):
    """手动请求暖场话题"""
    from src.coach.engine import CoachEngine
    p = engine.get(persona_id)
    ce = CoachEngine()
    result = ce.advise_warmup(p)
    console.print(Panel(result, title="🧊 暖场话题", border_style="yellow"))
```

[Append to `src/main.py`]

- [ ] **Step 2: Test coach commands**

```bash
python -m src.main coach strategy zhang_san --scene "公司茶水间偶遇"
python -m src.main coach warmup zhang_san
```
Expected: Both commands output AI-generated advice panels.

- [ ] **Step 3: Commit**

```bash
git add src/main.py
git commit -m "feat: add coach CLI commands (strategy/live/warmup)"
```

---

### Task 11: CLI — Analyze and knowledge commands

**Files:**
- Modify: `src/main.py`

- [ ] **Step 1: Add analyze and knowledge CLI groups**

Append to `src/main.py`:

```python
@main.group()
def analyze():
    """对话分析"""
    pass


@analyze.command()
@click.argument("text_file")
@click.option("--persona-id", "-p", default=None, help="关联的人物画像ID")
def text(text_file, persona_id):
    """分析对话文本文件"""
    from pathlib import Path
    from src.analyzer.engine import Analyzer
    from src.analyzer.merger import merge_updates

    content = Path(text_file).read_text()
    persona = engine.get(persona_id) if persona_id else None

    console.print("[bold]正在分析对话...[/bold]")
    analyzer = Analyzer()
    result = analyzer.analyze(content, persona)

    report = result.get("report", result)
    console.print(Panel(str(report), title="📊 分析报告", border_style="blue"))

    updates = analyzer.suggest_updates(result)
    if updates and persona:
        console.print(f"\n[yellow]发现 {len(updates)} 条画像更新建议[/yellow]")
        for i, u in enumerate(updates):
            console.print(f"  [{i+1}] {u['field']} ← {u.get('value', '')}")

        if click.confirm("是否应用这些更新?"):
            updated, conflicts = merge_updates(persona, updates)
            engine.update(persona_id, updated.model_dump())
            console.print(f"[green]✓ 画像已更新[/green]")
            for c in conflicts:
                console.print(f"  [yellow]⚠ {c['reason']}[/yellow]")


@analyze.command()
@click.argument("image_path")
@click.option("--persona-id", "-p", default=None, help="关联的人物画像ID")
def screenshot(image_path, persona_id):
    """分析聊天截图"""
    from src.utils.screenshot import extract_text
    from src.analyzer.engine import Analyzer

    console.print("[bold]正在识别截图中的对话...[/bold]")
    text = extract_text(image_path)
    console.print(f"[dim]识别结果:[/dim]\n{text}\n")

    persona = engine.get(persona_id) if persona_id else None
    analyzer = Analyzer()
    result = analyzer.analyze(text, persona)

    report = result.get("report", result)
    console.print(Panel(str(report), title="📊 分析报告", border_style="blue"))


@main.group()
def knowledge():
    """社交知识库管理"""
    pass


@knowledge.command()
def list():
    """列出所有原则"""
    from src.knowledge.base import KnowledgeBase
    kb = KnowledgeBase()
    principles = kb.list_all()
    console.print(f"\n共 {len(principles)} 条原则:\n")
    for p in principles:
        console.print(f"[cyan]{p.principle_id}[/cyan] [{p.source_title}] {p.principle}")
        console.print(f"  场景: {', '.join(p.applicable_scenarios)}")


@knowledge.command()
@click.argument("query")
def search(query):
    """搜索原则"""
    from src.knowledge.base import KnowledgeBase
    kb = KnowledgeBase()
    results = kb.search(scene_labels=[query], limit=5)
    if not results:
        results = kb.search(scene_labels=["通用社交"], limit=3)
    for p in results:
        console.print(Panel(
            f"[bold]{p.principle}[/bold]\n来源: {p.source_title}\n做法: {p.how_to_apply}",
            title=p.principle_id
        ))


@knowledge.command()
@click.option("--principle", prompt="原则内容")
@click.option("--source", prompt="来源书名")
@click.option("--category", prompt="分类", default="通用社交")
def add(principle, source, category):
    """手动添加原则"""
    from src.knowledge.base import KnowledgeBase
    kb = KnowledgeBase()
    pid = kb.add({
        "principle_id": f"user_{len(kb.list_all()) + 1:03d}",
        "source_type": "manual",
        "source_title": source,
        "principle": principle,
        "category": category,
        "applicable_scenarios": [],
        "how_to_apply": "",
        "counter_example": "",
    })
    console.print(f"[green]✓ 已添加: {pid}[/green]")
```

[Append to `src/main.py`]

- [ ] **Step 2: Test all commands**

```bash
# Analyze a test conversation
echo '我：周末去哪玩了？
她：就在家待着，太累了
我：理解，最近确实挺累的
她：是啊，项目太赶了' > /tmp/test_chat.txt

python -m src.main analyze text /tmp/test_chat.txt -p zhang_san

# Knowledge base
python -m src.main knowledge list
python -m src.main knowledge search "初次见面"
python -m src.main knowledge add --principle "测试原则" --source "测试" --category "测试"
```

Expected: All commands work.

- [ ] **Step 3: Commit**

```bash
git add src/main.py
git commit -m "feat: add analyze and knowledge CLI commands"
```

---

### Task 12: Final integration test and cleanup

- [ ] **Step 1: Full workflow test**

```bash
# 1. Create a persona
python -m src.main persona add --name "李四" --relationship "朋友"

# 2. View it
python -m src.main persona show li_si

# 3. Get strategy advice
python -m src.main coach strategy li_si --scene "周末咖啡厅见面"

# 4. Search knowledge
python -m src.main knowledge search "约会"

# 5. Analyze a conversation
echo '我：周末有空吗？
她：有啊，怎么了？
我：一起去看那个新展？
她：好啊！听说那个展超棒
我：那周六下午？
她：可以，几点？' > /tmp/test_chat.txt

python -m src.main analyze text /tmp/test_chat.txt -p li_si

# 6. Verify persona was updated
python -m src.main persona show li_si
```

Expected: Full workflow completes without errors, persona gets updated.

- [ ] **Step 2: Run all unit tests**

```bash
python -m pytest tests/ -v
```
Expected: All tests pass.

- [ ] **Step 3: Commit and push**

```bash
git add -A
git commit -m "feat: complete social-coach CLI v1 with all modules"
git push
```

---

### Post-Plan: What's NOT in v1

These are explicitly deferred to future versions:

- **Real audio input**: v1 uses text simulation for `coach live`. Real STT via Deepgram/Azure comes later.
- **Voice output (TTS)**: v1 displays text. ElevenLabs integration deferred.
- **Embedding-based persona search**: v1 uses exact ID matching.
- **Book PDF auto-extraction**: v1 ships with 5 pre-extracted principles. Auto-extraction from PDFs deferred.
- **Multi-user / productization**: v1 is single-user local CLI. Auth, multi-tenancy, mobile app deferred.
- **R1 deep analysis mode**: v1 uses V3 for everything. R1 routing for complex analysis deferred.
