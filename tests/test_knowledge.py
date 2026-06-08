import json
from pathlib import Path
from src.knowledge.base import KnowledgeBase, Principle


def test_search_by_scene(tmp_path):
    data_file = tmp_path / "test.json"
    data_file.write_text(json.dumps([{
        "principle_id": "t1", "principle": "测试原则1",
        "category": "约会", "applicable_scenarios": ["初次见面"]
    }, {
        "principle_id": "t2", "principle": "测试原则2",
        "category": "职场", "applicable_scenarios": ["职场"]
    }], ensure_ascii=False))

    kb = KnowledgeBase(data_file=data_file)
    results = kb.search(scene_labels=["约会"])
    assert len(results) == 1
    assert results[0].principle_id == "t1"


def test_add_returns_id(tmp_path):
    data_file = tmp_path / "test.json"
    kb = KnowledgeBase(data_file=data_file)
    pid = kb.add({"principle_id": "new_01", "principle": "新原则", "category": "测试"})
    assert pid == "new_01"
    assert len(kb.list_all()) == 1


def test_list_by_source(tmp_path):
    data_file = tmp_path / "test.json"
    data_file.write_text(json.dumps([{
        "principle_id": "t1", "principle": "测试", "source_title": "人性的弱点"
    }, {
        "principle_id": "t2", "principle": "测试2", "source_title": "影响力"
    }], ensure_ascii=False))

    kb = KnowledgeBase(data_file=data_file)
    results = kb.list_by_source("人性的弱点")
    assert len(results) == 1
    assert results[0].principle_id == "t1"
