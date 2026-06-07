# Social Coach — 云端 AI 社交指导系统

## 概述

AI 驱动的实时社交指导系统。用户在社交场合通过手机接收 AI 的实时提示（通过蓝牙耳机），帮助处理与不同人的互动。覆盖面对面聊天、多人聚会、线上聊天等场景。

### 核心体验

- **实时指导**：AI 在耳边悄悄告诉你怎么说、怎么读对方、聊什么
- **人物画像**：深度人物档案，记录性格、关系、策略，随互动自动优化
- **暖场救急**：冷场时主动推送话题

---

## 技术栈

- 语言：Python 3.11+
- AI：Claude API（Sonnet 为主，复杂场景 Opus）
- 存储：本地 JSON（第一版），后续迁移至 PostgreSQL + pgvector + Redis
- CLI：Click + Rich
- 依赖：anthropic SDK, Pillow（截图分析）

## 架构

```
┌─────────────────────────────────┐
│           CLI 界面               │
│  persona | coach | analyze      │
└──────────────┬──────────────────┘
               │
┌──────────────┴──────────────────┐
│          核心引擎                 │
│                                 │
│  ┌──────────┐  ┌──────────┐    │
│  │ 画像引擎  │  │ 教练引擎  │    │
│  │ Persona  │  │  Coach   │    │
│  └────┬─────┘  └────┬─────┘    │
│       │             │          │
│  ┌────┴─────────────┴─────┐   │
│  │      对话分析器          │   │
│  │       Analyzer          │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │      社交知识库           │   │
│  │       Knowledge          │   │
│  └─────────────────────────┘   │
└─────────────────────────────────┘
```

各模块通过明确定义的接口通信。教练引擎消费画像引擎、知识库、对话分析器的产出。

---

## 模块一：画像引擎（Persona Engine）

### 存储

JSON 文件，位于 `~/.social-agent/personas/{persona_id}.json`。

### Schema

```json
{
  "persona_id": "zhang_san_2024",
  "version": 3,
  "created_at": "2026-06-07T10:00:00Z",
  "updated_at": "2026-06-07T15:30:00Z",

  "basic": {
    "name": "张三",
    "alias": ["三哥"],
    "relationship": "同事",
    "closeness": 6,
    "scene_tags": ["职场", "饭局", "技术圈"],
    "first_met": "2024年3月，公司项目评审会",
    "avatar_url": null
  },

  "personality": {
    "traits": [
      {"trait": "外向", "confidence": 0.9, "evidence": "多次主动发起群聊..."}
    ],
    "mbti": {"type": "ENFJ", "confidence": 0.6, "source": "推断"},
    "communication_style": "直接、不绕弯子，不喜欢长篇铺垫",
    "emotional_triggers": {
      "positive": ["被认可技术能力", "聊到旅行和户外"],
      "negative": ["被打断发言", "谈及加班文化"]
    },
    "values": ["专业能力", "效率", "公平"]
  },

  "interaction": {
    "total_encounters": 12,
    "key_events": [
      {"date": "2026-05-20", "type": "重要", "summary": "一起吃饭时聊到想跳槽...", "tags": ["职业", "信任"]}
    ],
    "conversation_summary": "最近三个月主要在聊职业发展和行业动态...",
    "emotion_timeline": [
      {"date": "2026-06-01", "mood": "积极", "note": "主动约我吃饭"}
    ]
  },

  "goals": {
    "my_goal": "建立更深的信任关系，成为职场盟友",
    "their_attitude": "友善但保持职场距离",
    "opportunities": ["可以请TA帮忙内推", "每周三一起健身"],
    "risks": ["不要在工作群公开反对TA", "TA不喜欢聊私事"]
  },

  "strategies": {
    "topics_to_use": ["技术趋势", "公司八卦（轻度）", "健身"],
    "topics_to_avoid": ["加班", "薪资", "TA的家庭"],
    "communication_tips": ["有事说事，别铺垫", "用具体数据说话"],
    "gift_ideas": ["技术类书籍", "精品咖啡"]
  },

  "embedding": null
}
```

### 核心功能

- **CRUD**：手动创建/查看/编辑/删除画像
- **画像优化**：从对话分析器中接收更新建议，冲突合并后写入
- **冲突规则**：手动标注（confidence=1.0）永不被自动覆盖；同 confidence 级别合并去重

### 接口

```python
class PersonaEngine:
    def create(name: str, initial_data: dict = None) -> Persona
    def get(persona_id: str) -> Persona
    def update(persona_id: str, updates: dict) -> Persona
    def apply_updates(persona_id: str, suggestions: list[UpdateSuggestion]) -> Persona  # 带冲突检测
    def list() -> list[Persona]
    def search(query: str) -> list[Persona]  # 后续加 embedding 检索
```

---

## 模块二：教练引擎（Coach Engine）

### 四种模式

| 模式 | 用途 | 触发方式 |
|---|---|---|
| 策略型 | 见面前/中场休息，制定整体策略 | 手动 |
| 分析型 | 后台持续解读对方情绪和意图 | 自动（静默） |
| 话术型 | 卡壳时生成可直接说出口的回复 | 自动/手动 |
| 暖场型 | 冷场时推送破冰话题 | 自动（N秒沉默触发）/手动 |

### 模式一：策略型 Prompt 骨架

```
角色：资深社交策略顾问
输入：人物画像 JSON + 我的目标 + 场景信息
任务：
  1. 分析当前局势（TA态度、关系阶段、权力动态）
  2. 给出核心策略（1-2句）
  3. 推荐 3-5 个安全话题
  4. 标注 2-3 个禁忌
  5. 升级/撤退信号
约束：基于画像数据，不要泛泛而谈；信息不足时说明"推测"
```

### 模式二：分析型 Prompt 骨架

```
角色：实时社交翻译器
输入：人物画像 + 对方刚说的话 + 最近 5 轮上下文
任务：
  1. 解读情绪状态
  2. 分析话语真正意图
  3. 指出被忽略的微妙信号
  4. 给一句简短的应对方向
约束：引用对方原话关键词；不确定时宁可说"不确定"
```

### 模式三：话术型 Prompt 骨架

```
角色：口语出词器
输入：人物画像 + 对话上下文 + 我的说话风格
任务：生成 2-3 句可直接说出口的回复：
  1. 至少一个"安全牌"和一个"推进关系"话术
  2. 贴合我的说话风格，自然不 AI 感
  3. 注明每句话的意图（破冰/深入/试探/转移话题/幽默）
```

### 模式四：暖场型 Prompt 骨架

```
角色：社交破冰专家
输入：人物画像 + 对话上下文 + 冷场可能原因
任务：
  1. 分析冷场原因
  2. 生成三类候选话题：安全牌、升温牌、场景牌
  3. 附带选择理由
约束：话题必须基于画像数据中的安全话题/正向触发点
```

### 模式切换逻辑

- 分析型默认开启，后台持续运行
- 沉默超过 8 秒（可配置）→ 自动触发暖场型
- 用户主动请求 → 策略型/话术型
- 每次调用统一函数，由 mode 参数路由

### 知识库注入

每次调用教练引擎时，根据当前场景和人物特征从知识库检索相关原则，注入 Prompt 上下文窗口。

### 接口

```python
class CoachEngine:
    def advise_strategy(persona: Persona, scene: Scene) -> StrategyAdvice
    def advise_analysis(persona: Persona, utterance: str, context: list[str]) -> Analysis
    def advise_reply(persona: Persona, context: list[str], style: str) -> list[Reply]
    def advise_warmup(persona: Persona, context: list[str]) -> WarmupTopics
```

---

## 模块三：对话分析器（Analyzer）

### 输入输出

- **输入**：对话文本 + 目标人物画像（可选）+ 场景上下文
- **输出一**：对话分析报告
- **输出二**：画像更新建议

### 分析报告结构

```json
{
  "summary": "对话摘要...",
  "emotion_curve": [
    {"turn": 1, "speaker": "对方", "emotion": "中性"},
    {"turn": 4, "speaker": "对方", "emotion": "积极", "trigger": "聊到周末爬山"}
  ],
  "pivot_points": [
    {"turn": 4, "label": "气氛升温点", "what": "..."},
    {"turn": 6, "label": "微踩雷", "what": "..."}
  ],
  "engagement_score": 7.2,
  "my_performance": {
    "strengths": [...],
    "weaknesses": [...]
  },
  "relationship_signal": {
    "current": "...",
    "trend": "升温/平稳/降温",
    "next_move_hint": "..."
  }
}
```

### 画像更新建议结构

```json
{
  "persona_id": "zhang_san_2024",
  "updates": [
    {"field": "personality.traits", "action": "add", "value": {...}},
    {"field": "strategies.topics_to_use", "action": "add", "value": "攀岩"}
  ],
  "confidence_warnings": [
    {"field": "personality.mbti", "note": "证据不足，建议再观察"}
  ]
}
```

### 更新流程

```
对话文本 ──→ LLM 分析 ──→ 生成建议 ──→ 冲突检测 ──→ 用户确认 ──→ 写入画像
```

### 接口

```python
class Analyzer:
    def analyze(conversation: str, persona: Persona = None, scene: dict = None) -> AnalysisReport
    def suggest_updates(report: AnalysisReport, persona: Persona) -> list[UpdateSuggestion]
    def analyze_screenshot(image_path: str, persona: Persona = None) -> AnalysisReport  # 截图入口
```

---

## 模块四：社交知识库（Knowledge Base）

### 定位

教练引擎的上游知识来源。画像回答"这个人什么样"，知识库回答"这种情况怎么处理"。

### 知识结构

```json
{
  "principle_id": "p001",
  "source": {"type": "book", "title": "人性的弱点", "chapter": "如何让他人喜欢你"},
  "principle": "真诚地关心他人，而非假装关心",
  "category": "通用社交",
  "applicable_scenarios": ["初次见面", "维系关系"],
  "how_to_apply": "记住对方提到的细节，下次聊天时自然提起",
  "counter_example": "如果只记住信息但见面时不主动提起，对方会觉得你不关心",
  "related_principles": ["p003", "p007"],
  "effectiveness": null
}
```

### 知识源

| 类型 | 来源 | 提取方式 |
|---|---|---|
| 经典书籍 | 《人性的弱点》《亲密关系》《非暴力沟通》等 | 预提取（LLM 章节摘要 → 原则抽取） |
| 心理学理论 | 依恋理论、MBTI 体系 | 概念抽取 → 场景映射 |
| 用户总结 | 实践反馈/笔记 | 对话标注 → 策略沉淀 |

### 检索机制

- 文本匹配 + 语义检索（后续加 embedding）
- 按场景标签 + 人物标签检索相关原则
- 检索结果注入教练引擎 Prompt

### 第一版范围

- 内置 5 本书的核心原则（预提取，随项目自带）：
  - 《人性的弱点》— 戴尔·卡耐基
  - 《亲密关系》— 罗兰·米勒
  - 《非暴力沟通》— 马歇尔·卢森堡
  - 《男人来自火星，女人来自金星》— 约翰·格雷
  - 《影响力》— 罗伯特·西奥迪尼
- 用户可手动添加
- 教练引擎自动检索注入

### 接口

```python
class KnowledgeBase:
    def search(scene_labels: list[str], persona_traits: list[str], limit: int = 5) -> list[Principle]
    def add(principle: dict) -> str  # 返回 principle_id
    def list_by_source(source_title: str) -> list[Principle]
    def from_book(text: str, metadata: dict) -> list[Principle]  # 书籍提取（后续版本）
```

---

## CLI 接口设计

```bash
# 人物画像管理
social-agent persona add                     # 交互式创建画像
social-agent persona show <id>               # 查看画像
social-agent persona list                    # 列出所有画像
social-agent persona edit <id>               # 手动编辑

# 教练指导
social-agent coach strategy <id>             # 策略型：见面前分析
social-agent coach live <id>                 # 进入实时指导交互模式
social-agent coach warmup <id>               # 暖场：手动请求话题

# 对话分析
social-agent analyze text chat_log.txt       # 分析对话文本文件
social-agent analyze screenshot chat.png     # 分析聊天截图
social-agent analyze apply <id>              # 应用分析建议到画像

# 知识库
social-agent knowledge list                  # 列出所有原则
social-agent knowledge search <query>        # 搜索原则
social-agent knowledge add                   # 手动添加原则
```

### 实时指导交互模式（coach live）

> 第一版为文本模拟模式。用户在终端手动输入对方说的话，模拟实时对话。
> 后续版本接入麦克风和 STT 实现真正的实时音频指导。

```
$ social-agent coach live zhang_san_2024
📋 已加载画像：张三（同事）
🎯 当前目标：建立更深的信任关系
💡 建议策略：这次茶水间碰面，先聊轻松话题自然过渡...

[开始监听] 输入对方说的话，或输入 /help 查看命令：

> 她：最近项目好忙啊，感觉完全没时间休息。

🤔 分析：TA 在释放压力信号，可能是想找共鸣...
💬 安全回复：「确实，这个项目节奏太赶了。你负责那一块最近还顺利吗？」

> /warmup         # 手动请求暖场
🧊 安全话题：「对了，上次你说想学攀岩，后来去试了吗？」
  场景话题：「说起来这家咖啡比上次那家好喝」
  
> /exit
```

---

## 目录结构

```
social-agent/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI 入口
│   ├── persona/
│   │   ├── __init__.py
│   │   ├── engine.py        # PersonaEngine
│   │   ├── models.py        # Persona dataclass
│   │   └── storage.py       # JSON 文件读写
│   ├── coach/
│   │   ├── __init__.py
│   │   ├── engine.py        # CoachEngine（四种模式）
│   │   └── prompts.py       # Prompt 模板
│   ├── analyzer/
│   │   ├── __init__.py
│   │   ├── engine.py        # Analyzer
│   │   └── merger.py        # 冲突检测与合并
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── base.py          # KnowledgeBase
│   │   └── data/            # 预提取的原则数据
│   └── utils/
│       ├── __init__.py
│       ├── llm.py           # Claude API 封装
│       └── screenshot.py    # 截图 OCR
├── tests/
├── docs/superpowers/specs/2026-06-07-social-coach-design.md
├── requirements.txt
└── README.md
```

---

## 开发顺序

1. **项目骨架**：CLI 框架、配置管理、Claude API 封装
2. **画像引擎**：JSON 存储 + CRUD + Schema 验证
3. **教练引擎**：四种模式 Prompt + Claude 调用 + 知识库检索
4. **对话分析器**：对话文本分析 + 画像更新建议生成 + 冲突合并
5. **知识库**：预提取原则数据 + 检索 + 手动添加
6. **截图分析**：OCR + 对话提取 + 分析
