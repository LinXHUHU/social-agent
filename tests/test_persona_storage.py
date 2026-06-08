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
