"""Red-flag rules. Ported from CatNannyFramework tests/test_rules.py."""

from datetime import UTC, datetime, timedelta

from cat_health_signals import CatProfile, Event, redflags

NOW = datetime(2026, 10, 12, 12, 0, tzinfo=UTC)


def cat(**overrides) -> CatProfile:
    return CatProfile(**{"cat_id": "mochi", "name": "Mochi", "sex": "female", **overrides})


def event(type_: str, details: dict, ts: datetime = NOW, event_id: str = "e-current") -> Event:
    return Event(event_id=event_id, cat_id="mochi", ts=ts, type=type_, details=details, reporter="Alex")


def test_vomit_without_blood_or_low_energy_has_no_flags():
    assert redflags.check(event("vomit", {"content": "food", "has_blood": False}), [], cat(), NOW) == []


def test_vomit_with_blood_flags_call_vet_today():
    flags = redflags.check(event("vomit", {"content": "food", "has_blood": True}), [], cat(), NOW)
    assert flags[0].level == "vet_today" and flags[0].rule_id == "vomit_blood"
    assert flags[0].say_first.startswith("Please call your vet today.")


def test_vomit_with_low_energy_flags_call_vet_today():
    flags = redflags.check(event("vomit", {"low_energy": True}), [], cat(), NOW)
    assert [f.rule_id for f in flags] == ["vomit_low_energy"]


def test_third_vomit_in_24_hours_flags_call_vet_today():
    current = event("vomit", {"content": "food", "has_blood": False})
    history = [
        event("vomit", {"content": "food"}, NOW - timedelta(hours=2), "e1"),
        event("vomit", {"content": "liquid"}, NOW - timedelta(hours=6), "e2"),
    ]
    flags = redflags.check(current, history, cat(), NOW)
    assert any(f.rule_id == "vomit_three_times_24h" for f in flags)


def test_future_events_and_current_event_are_not_counted_as_history():
    current = event("vomit", {"content": "food", "has_blood": False})
    future = event("vomit", {}, NOW + timedelta(hours=1), "e-future")
    old = event("vomit", {}, NOW - timedelta(hours=30), "e-old")
    flags = redflags.check(current, [current, future, old], cat(), NOW)
    assert not any(f.rule_id == "vomit_three_times_24h" for f in flags)


def test_not_eating_for_24_hours_flags_call_vet_today():
    assert redflags.check(event("appetite", {"status": "not_eating", "hours_since_food": 24}), [], cat(), NOW)[0].rule_id == "not_eating_24h"
    assert redflags.check(event("appetite", {"status": "not_eating", "hours_since_food": 10}), [], cat(), NOW) == []
    assert redflags.check(event("appetite", {"status": "not_eating"}), [], cat(), NOW) == []


def test_male_cat_straining_without_urine_is_emergency():
    e = event("litter", {"straining": True, "passing_urine": False})
    flags = redflags.check(e, [], cat(sex="male"), NOW)
    assert flags[0].level == "emergency" and flags[0].rule_id == "male_cat_not_urinating"
    assert redflags.check(e, [], cat(sex="female"), NOW) == []


def test_flags_are_sorted_most_urgent_first():
    e = event("vomit", {"has_blood": True, "low_energy": True})
    flags = redflags.check(e, [], cat(), NOW)
    assert [f.rule_id for f in flags] == ["vomit_blood", "vomit_low_energy"]
    assert all(f.level == "vet_today" for f in flags)
