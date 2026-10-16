"""Detail schemas are strict. Ported from CatNannyFramework tests/test_schemas.py."""

import pytest
from pydantic import ValidationError

from cat_health_signals import SUPPORTED_EVENT_TYPES, AppetiteDetails, VomitDetails, schemas, validate_details


@pytest.mark.parametrize("data", [
    {"episode_count": -1}, {"episode_count": 1.5}, {"has_blood": "false"}, {"has_blood": 0},
    {"unexpected": True}, {"content": "diagnosis"},
])
def test_reject_invalid_observations(data):
    with pytest.raises(ValidationError):
        VomitDetails.model_validate(data)


def test_unknown_is_distinct_from_false():
    assert VomitDetails().has_blood is None
    assert VomitDetails(has_blood=False).has_blood is False


def test_appetite_bounds():
    with pytest.raises(ValidationError):
        AppetiteDetails(hours_since_food=-1)
    assert AppetiteDetails(status="not_eating", hours_since_food=30).hours_since_food == 30


def test_validate_details_fills_unknown_fields_with_none():
    assert validate_details("vomit", {"content": "food"}) == {
        "content": "food", "has_blood": None, "episode_count": None, "low_energy": None, "minutes_after_meal": None}
    with pytest.raises(KeyError):
        validate_details("weight", {"kg": 4})


def test_supported_types_and_field_descriptions():
    assert SUPPORTED_EVENT_TYPES == ("vomit", "appetite")
    text = schemas.describe_fields("vomit")
    assert "- has_blood:" in text and "- content:" in text
