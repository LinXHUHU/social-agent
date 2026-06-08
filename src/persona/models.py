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
