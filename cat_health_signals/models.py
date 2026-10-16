"""Data shapes shared by every rule.

These models are the contract between this package and anything that uses it
(the Cat Nanny MCP server, tests, other pet apps). Rules read `Event` and
`CatProfile` and return `FollowUp`, `Pattern`, `RedFlag` and `Assessment`.

Change field names here only together with the server: they are also what the
MCP tools return to the voice assistant.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

# --- inputs -----------------------------------------------------------------

EventType = Literal["vomit", "appetite", "litter", "energy", "meal", "medication", "weight", "food_change", "vet_visit"]
"""All known event types. Only those in `schemas.SUPPORTED_EVENT_TYPES` have a detail schema and questions today."""

EventSource = Literal["voice", "sensor", "seed"]


class Event(BaseModel):
    """One timestamped thing that happened to one cat.

    `details` holds the type-specific fields (for example `content` and
    `has_blood` for a vomit), validated by `schemas.DETAIL_MODELS`. A key with
    value None means "unknown"; it is never coerced to False.
    """

    event_id: str
    cat_id: str
    type: EventType
    ts: datetime
    details: dict[str, Any] = Field(default_factory=dict)
    reporter: str | None = None
    source: EventSource = "voice"


class CatProfile(BaseModel):
    cat_id: str
    name: str
    sex: Literal["female", "male", "unknown"] | None = "unknown"
    neutered: bool | None = None
    birth_year: int | None = None
    current_food: str | None = None
    conditions: list[str] = Field(default_factory=list)
    meals_per_day: int | None = None
    med_schedule: str | None = None
    """Free text for now, e.g. "1x daily". Make it structured if a rule needs it."""


# --- outputs ----------------------------------------------------------------


class FollowUp(BaseModel):
    """The single next question to ask about an event that is missing a required detail."""

    field: str
    question: str


class Pattern(BaseModel):
    """A pattern observed in the history. Always worded as an observation, never a cause."""

    kind: str
    summary: str
    evidence: dict[str, Any] = Field(default_factory=dict)


RedFlagLevel = Literal["emergency", "vet_today", "mention_next_visit"]
"""emergency = contact a vet now; vet_today = call the vet today; mention_next_visit = bring it up at the next visit."""

LEVEL_ORDER: dict[RedFlagLevel, int] = {"emergency": 0, "vet_today": 1, "mention_next_visit": 2}


class RedFlag(BaseModel):
    level: RedFlagLevel
    rule_id: str
    reason: str
    say_first: str
    """The sentence the assistant must say before anything else."""


class Assessment(BaseModel):
    """Everything the rules conclude about one newly logged (or updated) event."""

    follow_up: FollowUp | None = None
    red_flags: list[RedFlag] = Field(default_factory=list)
    patterns: list[Pattern] = Field(default_factory=list)
    pattern_note: str | None = None
    """One short line for the spoken reply, e.g. "3rd episode in 7 days"."""

    @property
    def top_level(self) -> RedFlagLevel | None:
        if not self.red_flags:
            return None
        return min((f.level for f in self.red_flags), key=lambda lvl: LEVEL_ORDER[lvl])

    @property
    def needs_family_alert(self) -> bool:
        return self.top_level in ("emergency", "vet_today")
