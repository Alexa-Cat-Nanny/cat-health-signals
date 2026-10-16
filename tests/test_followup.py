"""Follow-up questions: one at a time, in order, skipping details marked unknown."""

from cat_health_signals import followup


def test_vomit_questions_in_order():
    q = followup.next_question("vomit", {})
    assert q is not None and q.field == "content"
    q = followup.next_question("vomit", {"content": "food"})
    assert q is not None and q.field == "has_blood" and q.question == "Did you see any blood?"


def test_false_counts_as_answered_and_none_does_not():
    assert followup.next_question("vomit", {"content": "food", "has_blood": False}).field == "episode_count"
    assert followup.next_question("vomit", {"content": "food", "has_blood": None}).field == "has_blood"


def test_unknown_fields_are_skipped():
    details = {"content": "food", "has_blood": None}
    assert followup.missing_fields("vomit", details, unknown_fields=["has_blood"]) == ["episode_count", "low_energy"]
    assert followup.next_question("vomit", details, unknown_fields=["has_blood"]).field == "episode_count"


def test_no_question_when_complete():
    details = {"content": "food", "has_blood": False, "episode_count": 2, "low_energy": False}
    assert followup.next_question("vomit", details) is None
    assert followup.next_question("appetite", {"status": "eating_less", "hours_since_food": 12}) is None


def test_unsupported_type_has_no_questions():
    assert followup.next_question("weight", {}) is None
