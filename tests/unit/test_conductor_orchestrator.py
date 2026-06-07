"""Unit tests — invisible conductor step parsing and heuristics."""

from __future__ import annotations

from src.agents.conductor_orchestrator import (
    ConductorState,
    _heuristic_step,
    _parse_step_json,
    chunk_is_redundant,
    conductor_next_step,
    conductor_opening_line,
    conductor_status_text,
    dedupe_answer_against_chunks,
)


def test_parse_step_json_emit_message() -> None:
    raw = '{"action":"emit_message","message_brief":"Say you are searching now","wait_seconds":5}'
    step = _parse_step_json(raw)
    assert step is not None
    assert step.action == "emit_message"
    assert "searching" in (step.message_brief or "")


def test_parse_step_json_complete_alias() -> None:
    step = _parse_step_json('{"action":"finish","reason":"done"}')
    assert step is not None
    assert step.action == "complete"


def test_heuristic_progress_does_not_repeat_scope() -> None:
    state = ConductorState(
        query="ofertas gatos y tortugas 20-50€",
        site_id=15,
        lane="catalog_search",
        tick_index=2,
        elapsed_seconds=10,
        messages_sent=(
            "Solo perros y gatos — busco ofertas para tu gato.",
            "Revisando el catálogo…",
        ),
        catalog_running=True,
        catalog_done=False,
    )
    step = _heuristic_step(state)
    assert step.action == "emit_message"
    brief = (step.message_brief or "").lower()
    assert "tortuga" not in brief
    assert "solo" not in brief or "perros" not in brief


def test_conductor_next_step_uses_heuristic_when_llm_disabled(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ZOOPLUS_AGENT_CASCADE", "0")
    state = ConductorState(
        query="dry food puppy",
        site_id=3,
        lane="catalog_search",
        tick_index=0,
        elapsed_seconds=0,
        messages_sent=(),
        catalog_running=False,
        catalog_done=False,
        shopper_status="Looking for dry puppy food",
    )

    def _fail(*_a, **_k):
        return type("R", (), {"value": None, "raw": None})()

    monkeypatch.setattr("src.agents.conductor_orchestrator.run_agent_cascade", _fail)

    def _noop(*_a, **_k):
        return ""

    monkeypatch.setattr("src.agents.conductor_orchestrator.run_opencode_agent", _noop)

    step = conductor_next_step(state)
    assert step.action in ("emit_message", "start_catalog", "complete", "wait")


def test_conductor_opening_line_multi_species_spanish() -> None:
    text = conductor_opening_line(
        "precios hamsters tortugas caballos perros y gatos hasta 50€",
        15,
    )
    assert "hamster" in text.lower()
    assert "tortuga" in text.lower()
    assert "caballo" in text.lower()
    assert "perros y gatos" in text.lower()
    assert "50" in text


def test_conductor_status_text_scope_once_spanish() -> None:
    state = ConductorState(
        query="opciones perros y tortugas 20-50€",
        site_id=15,
        lane="catalog_search",
        tick_index=0,
        elapsed_seconds=0,
        messages_sent=(),
        catalog_running=True,
        catalog_done=False,
    )
    text = conductor_status_text(state)
    assert "tortuga" in text.lower()
    assert "perros y gatos" in text.lower()


def test_conductor_status_text_progress_no_scope_repeat() -> None:
    state = ConductorState(
        query="opciones perros y tortugas",
        site_id=15,
        lane="catalog_search",
        tick_index=2,
        elapsed_seconds=10,
        messages_sent=("Solo perros y gatos — no tortugas.",),
        catalog_running=True,
        catalog_done=False,
    )
    text = conductor_status_text(state)
    assert "tortuga" not in text.lower()


def test_chunk_is_redundant_detects_scope_repeat() -> None:
    prior = ("Solo tenemos productos para perros y gatos — no tortugas.",)
    dup = "En nuestra tienda solo ofrecemos productos para perros y gatos."
    assert chunk_is_redundant(dup, prior)


def test_dedupe_answer_strips_scope_after_chunk() -> None:
    chunks = ("¡Con gusto! Solo tenemos productos para perros y gatos — no tortugas.",)
    answer = (
        "Hola, soy el zooplus Assistant. En nuestra tienda solo ofrecemos productos "
        "para perros y gatos, por lo que no disponemos de opciones para tortugas. "
        "Para tu perro te recomiendo Eukanuba."
    )
    trimmed = dedupe_answer_against_chunks(answer, chunks)
    assert "tortuga" not in trimmed.lower()
    assert "Eukanuba" in trimmed


def test_dedupe_answer_strips_como_tu_greeting() -> None:
    chunks = ("¡Con gusto! Solo tenemos productos para perros y gatos — no tortugas.",)
    answer = (
        "Hola, como tu zooplus Assistant, estaré encantado de ayudarte. "
        "Te recomiendo Cosma Pure y Purizon para felinos."
    )
    trimmed = dedupe_answer_against_chunks(answer, chunks)
    assert "zooplus assistant" not in trimmed.lower()
    assert "Cosma" in trimmed
