"""cat-health-signals: deterministic follow-ups, patterns and red flags from a cat's health log.

Pure functions only: no I/O, no clock, no LLM. Pass `now` in explicitly so the
same input always gives the same output.
"""

from __future__ import annotations

from datetime import datetime

from . import followup, patterns, redflags, schemas, summary
from .models import (
    Assessment,
    CatProfile,
    Event,
    EventType,
    FollowUp,
    Pattern,
    RedFlag,
    RedFlagLevel,
)
from .schemas import DETAIL_MODELS, SUPPORTED_EVENT_TYPES, AppetiteDetails, VomitDetails, validate_details

__version__ = "0.2.0"

__all__ = [
    "Assessment",
    "AppetiteDetails",
    "CatProfile",
    "DETAIL_MODELS",
    "Event",
    "EventType",
    "FollowUp",
    "Pattern",
    "RedFlag",
    "RedFlagLevel",
    "SUPPORTED_EVENT_TYPES",
    "VomitDetails",
    "assess",
    "followup",
    "patterns",
    "redflags",
    "schemas",
    "summary",
    "validate_details",
]


def assess(event: Event, history: list[Event], cat: CatProfile, now: datetime,
           unknown_fields: list[str] | set[str] = ()) -> Assessment:
    """Everything the rules conclude about one event.

    `history` is the cat's recent events (at least 24 hours, ideally 60 days) and
    may include `event` itself. `unknown_fields` are details the user said they
    could not answer, so they are not asked again.
    """
    return Assessment(
        follow_up=followup.next_question(event.type, event.details, unknown_fields),
        red_flags=redflags.check(event, history, cat, now),
        patterns=patterns.find_patterns(history, cat, now),
        pattern_note=patterns.quick_note(event, history, now),
    )
