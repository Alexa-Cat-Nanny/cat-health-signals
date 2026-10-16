"""Red flags: situations where the assistant must recommend a vet before saying anything else.

Ported from CatNannyFramework `catnanny/domain/rules.py`. Every rule is a plain
function `(event, history, cat, now) -> RedFlag | None` registered in RULES, so
each can be unit-tested on its own. Levels (see models.RedFlagLevel):

- emergency: contact a vet or emergency clinic now
- vet_today: call the vet today
- mention_next_visit: bring it up at the next visit

These conditions follow common veterinary guidance and must be reviewed by a
veterinarian before any real-world use. They describe observations; they never diagnose.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta

from .models import LEVEL_ORDER, CatProfile, Event, RedFlag

Rule = Callable[[Event, list[Event], CatProfile, datetime], RedFlag | None]

CALL_VET_TODAY = "Please call your vet today."


def vomit_blood(event: Event, history: list[Event], cat: CatProfile, now: datetime) -> RedFlag | None:
    if event.type == "vomit" and event.details.get("has_blood") is True:
        return RedFlag(level="vet_today", rule_id="vomit_blood",
                       reason="Blood was seen in the vomit.",
                       say_first=f"{CALL_VET_TODAY} Vomit with blood is worth prompt veterinary advice.")
    return None


def vomit_low_energy(event: Event, history: list[Event], cat: CatProfile, now: datetime) -> RedFlag | None:
    if event.type == "vomit" and event.details.get("low_energy") is True:
        return RedFlag(level="vet_today", rule_id="vomit_low_energy",
                       reason="Vomiting together with low energy.",
                       say_first=f"{CALL_VET_TODAY} Vomiting together with low energy can be concerning.")
    return None


def vomit_three_times_24h(event: Event, history: list[Event], cat: CatProfile, now: datetime) -> RedFlag | None:
    """At least the third vomiting episode within 24 hours before this one (earlier events only)."""
    if event.type != "vomit":
        return None
    earlier = [e for e in history
               if e.event_id != event.event_id and e.type == "vomit"
               and timedelta(0) <= event.ts - e.ts <= timedelta(hours=24)]
    if len(earlier) >= 2:
        return RedFlag(level="vet_today", rule_id="vomit_three_times_24h",
                       reason="At least three vomiting episodes in 24 hours.",
                       say_first=f"{CALL_VET_TODAY} This is at least the third vomiting episode in 24 hours.")
    return None


def not_eating_24h(event: Event, history: list[Event], cat: CatProfile, now: datetime) -> RedFlag | None:
    if event.type != "appetite":
        return None
    hours = event.details.get("hours_since_food")
    if isinstance(hours, int | float) and hours >= 24:
        return RedFlag(level="vet_today", rule_id="not_eating_24h",
                       reason="The cat has not eaten normally for 24 hours or more.",
                       say_first=f"{CALL_VET_TODAY} A cat not eating for more than 24 hours should be checked.")
    return None


def male_cat_not_urinating(event: Event, history: list[Event], cat: CatProfile, now: datetime) -> RedFlag | None:
    """Kept from the original rule set although `litter` is not yet a conversational event type."""
    if event.type != "litter" or cat.sex != "male":
        return None
    if event.details.get("straining") is True and event.details.get("passing_urine") is False:
        return RedFlag(level="emergency", rule_id="male_cat_not_urinating",
                       reason="A male cat straining without passing urine.",
                       say_first="This can be an emergency. Please contact a vet or emergency clinic now.")
    return None


RULES: list[Rule] = [
    male_cat_not_urinating,
    vomit_blood,
    vomit_low_energy,
    vomit_three_times_24h,
    not_eating_24h,
]


def check(event: Event, history: list[Event], cat: CatProfile, now: datetime) -> list[RedFlag]:
    """Run every rule against the new event; most urgent first. `history` may include `event`."""
    flags = [flag for rule in RULES if (flag := rule(event, history, cat, now)) is not None]
    return sorted(flags, key=lambda f: LEVEL_ORDER[f.level])
