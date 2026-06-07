"""Unit tests — conductor playbook MD parse and silent learning."""

from __future__ import annotations

import pytest
from src.agents import stream_voice_registry as svr

pytestmark = pytest.mark.unit


@pytest.fixture
def playbook(tmp_path, monkeypatch: pytest.MonkeyPatch):
    seed = svr.PLAYBOOK_SEED.read_text(encoding="utf-8")
    live = tmp_path / "conductor_playbook.md"
    live.write_text(seed, encoding="utf-8")
    monkeypatch.setattr(svr, "PLAYBOOK_PATH", live)
    svr.reload_stream_voice_registry()
    yield live
    svr.reload_stream_voice_registry()


def test_playbook_loads_species() -> None:
    svr._ensure_playbook()
    reg = svr.load_stream_voice_registry()
    assert reg["species"]
    assert any(e.label_es == "tortugas" for e in reg["species"])


def test_probe_social_skips_catalog_opening(playbook) -> None:
    assert svr.probe_instant_lane("hola que tal", 15) == "social"
    assert svr.probe_instant_lane("hello how are you", 3) == "social"


def test_probe_catalog_for_product_query(playbook) -> None:
    probe = svr.probe_instant_lane("best dry food for puppy", 3)
    assert probe in ("catalog", "pending")


def test_greeting_probe_not_catalog(playbook) -> None:
    assert svr.probe_instant_lane("hola", 15) == "social"


def test_format_opening_multi_species(playbook) -> None:
    text = svr.format_opening_line(
        "precios hamsters tortugas caballos perros y gatos hasta 50€",
        15,
    )
    assert "hamster" in text.lower()
    assert "tortuga" in text.lower()
    assert "caballo" in text.lower()
    assert "perros y gatos" in text.lower()


def test_conductor_appends_learned_to_md(playbook) -> None:
    svr.record_stream_voice_learning(
        category="greeting_markers",
        phrase="Hola, como tu zooplus Assistant",
        reason="greeting_repeated_in_final",
        source="test",
    )
    body = playbook.read_text(encoding="utf-8")
    assert "Hola, como tu zooplus Assistant" in body
    assert "## learned_greeting_markers" in body
    reg = svr.load_stream_voice_registry()
    assert "hola, como tu zooplus assistant" in reg["greeting_markers"]


def test_dedupe_learns_into_playbook(playbook) -> None:
    chunks = ("¡Con gusto! Solo tenemos productos para perros y gatos — no tortugas.",)
    answer = (
        "Hola, como tu zooplus Assistant, estaré encantado. "
        "Te recomiendo Cosma Pure para gatos."
    )
    trimmed = svr.dedupe_answer_against_chunks(answer, chunks)
    assert "zooplus assistant" not in trimmed.lower()
    assert "Cosma" in trimmed
    assert "learned_" in playbook.read_text(encoding="utf-8")
