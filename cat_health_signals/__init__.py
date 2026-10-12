"""cat-health-signals: deterministic follow-ups, patterns and red flags from a cat's health log.

Pure functions only: no I/O, no clock, no LLM. Pass `now` in explicitly so the
same input always gives the same output.
"""

from __future__ import annotations

from datetime import datetime

from . import fields, followup, patterns, redflags, summary
from .models import (
    Assessment,
    CareEventType,
    CatProfile,
    Event,
    EventType,
    FollowUp,
    HealthEventType,
    Pattern,
    RedFlag,
    RedFlagLevel,
)

__version__ = "0.1.0"

__all__ = [
    "Assessment",
    "CareEventType",
    "CatProfile",
    "Event",
    "EventType",
    "FollowUp",
    "HealthEventType",
    "Pattern",
    "RedFlag",
    "RedFlagLevel",
    "assess",
    "fields",
    "followup",
    "patterns",
    "redflags",
    "summary",
]


def assess(event: Event, history: list[Event], cat: CatProfile, now: datetime) -> Assessment:
    """Everything the rules conclude about one event.

    `history` is the cat's recent events (at least 60 days) and must already
    include `event` itself.
    """
    return Assessment(
        follow_up=followup.next_question(event),
        red_flags=redflags.check(event, history, cat, now),
        patterns=patterns.find_patterns(history, cat, now),
        pattern_note=patterns.quick_note(event, history, now),
    )
