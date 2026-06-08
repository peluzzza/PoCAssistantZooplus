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


def test_probe_social_help_not_catalog(playbook) -> None:
    assert svr.probe_instant_lane("me puedes ayudar", 15) == "social"
    assert svr.probe_instant_lane("can you help me", 3) == "social"


def test_social_help_auto_learn(playbook) -> None:
    novel = "me echas una mano con la tienda"
    assert not svr.matches_playbook_social_help(novel)
    svr.learn_social_help_phrase(novel)
    assert svr.matches_playbook_social_help(novel)
    assert "## learned_social_help" in playbook.read_text(encoding="utf-8")


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


def test_dedupe_strips_greeting_after_progress_only_chunks(playbook) -> None:
    """Progress chunks without hola/claro still mean conversation started."""
    chunks = ("Sigue buscando en el catálogo, un momento más…",)
    answer = (
        "Hola, soy el zooplus Assistant. Lamentablemente no dispongo de productos para iguanas, "
        "ya que solo puedo ofrecerte artículos del catálogo de perros y gatos."
    )
    trimmed = svr.dedupe_answer_against_chunks(answer, chunks)
    assert "hola" not in trimmed.lower().split(".")[0]
    assert "zooplus assistant" not in trimmed.lower()[:40]
    assert "iguanas" in trimmed.lower()


def test_dynamic_species_capibara_without_playbook_seed(playbook) -> None:
    """Species not in seed MD — inferred from 'y para X' and auto-learned."""
    seed = svr.PLAYBOOK_SEED.read_text(encoding="utf-8")
    assert "capibara" not in seed.lower()
    labels = svr.infer_non_catalog_species_labels("y para capibaras tienes?", 15, learn=True)
    assert "capibaras" in labels
    body = playbook.read_text(encoding="utf-8")
    assert "capibara" in body.lower()


def test_dynamic_species_iguana(playbook) -> None:
    labels = svr.infer_non_catalog_species_labels("y para iguanas tienes?", 15, learn=False)
    assert "iguanas" in labels


def test_in_scope_pets_not_flagged(playbook) -> None:
    assert not svr.mentions_non_catalog_species("y para perros con estomago sensible", 15)
    assert not svr.mentions_non_catalog_species("best dry food for puppy", 3)


def test_is_continuation_query() -> None:
    assert svr.is_continuation_query("y para iguanas tienes?")
    assert svr.is_continuation_query("and for dogs under 20€")
    assert not svr.is_continuation_query("hola que tal")


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
