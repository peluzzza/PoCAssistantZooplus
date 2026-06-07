"""Unit tests — invisible conductor step parsing and heuristics."""

from __future__ import annotations

from src.agents.conductor_orchestrator import (
    ConductorState,
    _heuristic_step,
    _parse_step_json,
    conductor_next_step,
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
    monkeypatch.setattr("src.agents.conductor_orchestrator.run_opencode_agent", lambda *_a, **_k: "")

    step = conductor_next_step(state)
    assert step.action in ("emit_message", "start_catalog", "complete", "wait")
