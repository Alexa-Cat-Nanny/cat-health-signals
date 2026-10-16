"""Follow-up questions: the ordered list of details worth asking about for each event type.

Ported from CatNannyFramework `catnanny/domain/questionnaire.py`. Questions are
asked one at a time, in order. A detail the user explicitly could not answer
("not sure") is recorded in `unknown_fields` and is not asked again.
"""

from __future__ import annotations

from .models import FollowUp

QUESTIONS: dict[str, list[tuple[str, str]]] = {
    "vomit": [
        ("content", "Was it food, a hairball, liquid, or foam?"),
        ("has_blood", "Did you see any blood?"),
        ("episode_count", "How many vomiting episodes are you recording?"),
        ("low_energy", "Did you notice lower energy than usual?"),
    ],
    "appetite": [
        ("status", "Is your cat not eating at all, or eating less than usual?"),
        ("hours_since_food", "About how many hours since your cat last ate normally?"),
    ],
}


def missing_fields(event_type: str, details: dict, unknown_fields: list[str] | set[str] = ()) -> list[str]:
    """Details not yet answered, in asking order, skipping ones marked unknown."""
    return [key for key, _ in QUESTIONS.get(event_type, [])
            if details.get(key) is None and key not in unknown_fields]


def next_question(event_type: str, details: dict, unknown_fields: list[str] | set[str] = ()) -> FollowUp | None:
    """The single next question to ask, or None when every detail is answered or marked unknown.

    A value of False counts as answered ("no blood" is an answer); only None is missing.
    """
    missing = missing_fields(event_type, details, unknown_fields)
    if not missing:
        return None
    key = missing[0]
    return FollowUp(field=key, question=dict(QUESTIONS[event_type])[key])
