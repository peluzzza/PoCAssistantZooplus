"""Unit tests — session turn invalidation."""

from __future__ import annotations

from src.cache.session_turn import bump_session_turn, is_current_turn


def test_bump_invalidates_previous_turn() -> None:
    sid = "unit-test-session"
    t1 = bump_session_turn(sid)
    assert is_current_turn(sid, t1)
    t2 = bump_session_turn(sid)
    assert t2 == t1 + 1
    assert is_current_turn(sid, t2)
    assert not is_current_turn(sid, t1)
