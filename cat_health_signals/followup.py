"""Follow-up questions: which details each event type must have, and what to ask when one is missing.

TODO(team): fill REQUIRED_DETAILS once the field list is agreed. The single
vomit entry below is an EXAMPLE so the end-to-end flow can be tested; replace it.
"""

from __future__ import annotations

from .models import Event, EventType, FollowUp

REQUIRED_DETAILS: dict[EventType, list[tuple[str, str]]] = {
    # event type -> ordered list of (details key, question to ask if the key is missing)
    "vomit": [
        ("content", "Was it food, hairball, or liquid?"),  # EXAMPLE ONLY
    ],
}


def next_question(event: Event) -> FollowUp | None:
    """Return the first missing required detail for this event, or None if nothing is missing.

    Asks at most one question per call, in the order listed in REQUIRED_DETAILS.
    A detail counts as present when its key exists, even if the value is False
    (an answer of "no blood" is still an answer).
    """
    for field, question in REQUIRED_DETAILS.get(event.type, []):
        if field not in event.details or event.details[field] is None:
            return FollowUp(field=field, question=question)
    return None
