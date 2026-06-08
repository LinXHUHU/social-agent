"""Self-profile — the user's own persona for coaching personalization."""
import json
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field

SELF_FILE = Path.home() / ".social-agent" / "self.json"


class SelfTraits(BaseModel):
    traits: list[str] = Field(default_factory=list)
    communication_style: str = ""
    catchphrases: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)


class SelfProfile(BaseModel):
    name: str = "我"
    personality: SelfTraits = Field(default_factory=SelfTraits)
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


def load() -> SelfProfile:
    if SELF_FILE.exists():
        with open(SELF_FILE) as f:
            data = json.load(f)
        return SelfProfile(**data)
    return SelfProfile()


def save(profile: SelfProfile):
    SELF_FILE.parent.mkdir(parents=True, exist_ok=True)
    profile.updated_at = datetime.now().isoformat()
    with open(SELF_FILE, "w") as f:
        json.dump(profile.model_dump(), f, ensure_ascii=False, indent=2, default=str)


def get_style() -> str:
    """Return a natural-language summary of my communication style for prompts."""
    p = load()
    parts = [p.personality.communication_style] if p.personality.communication_style else []
    if p.personality.traits:
        parts.append("性格特征: " + ", ".join(p.personality.traits))
    if p.personality.catchphrases:
        parts.append("常用口头禅: " + ", ".join(p.personality.catchphrases))
    return "; ".join(parts) or "自然随意"
