"""Red flags: situations where the assistant must recommend a vet before saying anything else.

Three levels (see models.RedFlagLevel). `emergency` and `vet_today` also notify
the family. Every rule is a plain function `(event, history, cat, now) -> RedFlag | None`
registered in RULES, so each can be unit-tested on its own.

TODO(team): replace the EXAMPLE rule with the agreed rule table, and have a vet
review the conditions before the demo.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from .models import LEVEL_ORDER, CatProfile, Event, RedFlag

Rule = Callable[[Event, list[Event], CatProfile, datetime], RedFlag | None]


def _example_blood_in_vomit(event: Event, history: list[Event], cat: CatProfile, now: datetime) -> RedFlag | None:
    """EXAMPLE ONLY: vomit with blood -> call the vet today."""
    if event.type == "vomit" and event.details.get("blood") is True:
        return RedFlag(
            level="vet_today",
            rule_id="example_blood_in_vomit",
            reason="Blood was seen in the vomit.",
            say_first="Please call your vet today.",
        )
    return None


RULES: list[Rule] = [
    _example_blood_in_vomit,
]


def check(event: Event, history: list[Event], cat: CatProfile, now: datetime) -> list[RedFlag]:
    """Run every rule against the new event; most urgent first. `history` includes `event`."""
    flags = [flag for rule in RULES if (flag := rule(event, history, cat, now)) is not None]
    return sorted(flags, key=lambda f: LEVEL_ORDER[f.level])
