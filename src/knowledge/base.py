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
