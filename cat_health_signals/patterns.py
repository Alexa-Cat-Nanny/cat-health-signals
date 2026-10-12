"""Patterns found in a cat's history (frequency change, after meals, after a food change, weight trend).

TODO(team): implement the agreed patterns in `find_patterns`. Each one must
only be reported when its threshold is met, and its `summary` must describe
what was observed ("4 of the last 5 episodes were within 30 minutes of a meal"),
never a cause.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from .models import CatProfile, Event, EventType, Pattern


def count_recent(history: list[Event], event_type: EventType, now: datetime, days: int) -> int:
    """How many events of this type happened in the `days` days before `now`."""
    since = now - timedelta(days=days)
    return sum(1 for e in history if e.type == event_type and since <= e.ts <= now)


def find_patterns(history: list[Event], cat: CatProfile, now: datetime, days: int = 30) -> list[Pattern]:
    """All patterns that meet their reporting threshold in the last `days` days. Stub: returns none yet."""
    return []


def quick_note(event: Event, history: list[Event], now: datetime) -> str | None:
    """A short spoken line about how this event compares with recent history.

    Kept deliberately simple (a count); the real patterns live in find_patterns.
    """
    if event.type not in ("vomit", "appetite", "litter", "energy"):
        return None
    n = count_recent(history, event.type, now, days=7)
    if n <= 1:
        return None
    return f"{_ordinal(n)} {event.type} event in the last 7 days"


def _ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
