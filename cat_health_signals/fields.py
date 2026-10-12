"""The `details` keys each event type may carry. THIS IS THE SCHEMA THE TEAM IS DEFINING.

The Cat Nanny server builds its tool descriptions from this table, so the voice
assistant knows which keys to extract from what the user said. One place to edit:
add a key here, use it in a rule, and the assistant starts filling it in.

Format: event type -> {details key: description shown to the assistant}.
Put allowed values in the description ("one of: food, hairball, liquid, foam").

DRAFT: copied from the design doc; confirm every key is used by a rule.
"""

from __future__ import annotations

from .models import EventType

DETAIL_FIELDS: dict[EventType, dict[str, str]] = {
    # health observations
    "vomit": {
        "content": "what came up, one of: food, hairball, liquid, foam",
        "blood": "true if any blood was seen, false if the user said there was none",
        "minutes_after_meal": "integer minutes between the last meal and the vomiting, if the user said",
    },
    "appetite": {
        "level": "one of: normal, less, none",
        "hours_since_last_meal": "integer hours since the cat last ate normally, if known",
    },
    "litter": {
        "urine": "one of: normal, less, none",
        "stool": "one of: normal, soft, diarrhea, none",
        "straining": "true if the cat was straining in the litter box",
    },
    "energy": {
        "level": "one of: normal, low, hiding",
    },
    # care events
    "meal": {"food": "what was fed, if mentioned"},
    "medication": {"name": "medicine name, if mentioned", "dose": "dose as said, if mentioned"},
    "weight": {"kg": "weight in kilograms as a number (convert pounds: lb / 2.205)"},
    "food_change": {"from": "previous food", "to": "new food"},
    "vet_visit": {"outcome": "what the vet said, in the user's words"},
}


def describe(types: tuple[str, ...]) -> str:
    """Human-readable list of keys per type, for tool descriptions."""
    lines = []
    for t in types:
        keys = DETAIL_FIELDS.get(t, {})  # type: ignore[call-overload]
        if keys:
            lines.append(f"- {t}: " + "; ".join(f"{k} ({v})" for k, v in keys.items()))
    return "\n".join(lines)
