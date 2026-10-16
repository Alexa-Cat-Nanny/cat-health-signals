"""Contract tests: the shapes and guarantees the Cat Nanny server relies on."""

from datetime import UTC, datetime, timedelta

from cat_health_signals import Assessment, CatProfile, Event, assess
from cat_health_signals.summary import build_summary

NOW = datetime(2026, 10, 12, 18, 0, tzinfo=UTC)
CAT = CatProfile(cat_id="mochi", name="Mochi", sex="female")


def ev(i: int, type_: str, days_ago: float = 0, **details) -> Event:
    return Event(event_id=f"e{i}", cat_id="mochi", type=type_, ts=NOW - timedelta(days=days_ago), details=details)


def test_assess_returns_assessment_and_is_deterministic():
    e = ev(1, "vomit", content="food")
    a1 = assess(e, [e], CAT, NOW)
    a2 = assess(e, [e], CAT, NOW)
    assert isinstance(a1, Assessment)
    assert a1 == a2


def test_missing_required_detail_gives_one_question():
    e = ev(1, "vomit")
    a = assess(e, [e], CAT, NOW)
    assert a.follow_up is not None and a.follow_up.field == "content"


def test_unknown_fields_are_not_asked_again():
    e = ev(1, "vomit", content="food", has_blood=None)
    assert assess(e, [e], CAT, NOW, unknown_fields={"has_blood"}).follow_up.field == "episode_count"


def test_red_flag_and_alert_level():
    e = ev(1, "vomit", content="food", has_blood=True)
    a = assess(e, [e], CAT, NOW)
    assert a.top_level == "vet_today"
    assert a.needs_family_alert
    assert a.red_flags[0].say_first.startswith("Please call your vet today.")


def test_quick_note_counts_last_7_days():
    hist = [ev(1, "vomit", 1, content="food"), ev(2, "vomit", 3, content="food"), ev(3, "vomit", 20, content="food")]
    new = ev(4, "vomit", 0, content="food")
    assert assess(new, [*hist, new], CAT, NOW).pattern_note == "3rd vomit event in the last 7 days"


def test_summary_counts_and_weight():
    hist = [
        ev(1, "vomit", 2), ev(2, "vomit", 5), ev(3, "vomit", 40),
        ev(4, "weight", 25, kg=4.2), ev(5, "weight", 1, kg=4.0),
        ev(6, "food_change", 9, **{"from": "A", "to": "B"}),
    ]
    s = build_summary(hist, CAT, NOW, days=30)
    assert len(s.timeline) == 30
    vomit = next(c for c in s.comparisons if c.event_type == "vomit")
    assert (vomit.current, vomit.previous) == (2, 1)
    assert s.weight is not None and s.weight.change_pct == -4.8
    assert s.food_changes[0]["to"] == "B"
