"""Observation detail schemas: the fields each supported event type may carry.

Ported from CatNannyFramework `catnanny/domain/schemas.py`. These are strict on
purpose: an unknown observation stays `None` (not False), extra keys are
rejected, and strings are never coerced into booleans or numbers. A voice
assistant that fills these from speech must therefore only pass what the user
actually said.

Supported in conversation today: `vomit` and `appetite`.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool


class Details(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class VomitDetails(Details):
    content: Literal["food", "hairball", "liquid", "foam", "other"] | None = Field(
        default=None, description="What came up: food, hairball, liquid, foam or other")
    has_blood: StrictBool | None = Field(
        default=None, description="true if blood was seen, false if the user said there was none")
    episode_count: int | None = Field(
        default=None, ge=1, le=1000, description="How many vomiting episodes this observation covers")
    low_energy: StrictBool | None = Field(
        default=None, description="true if the cat also seemed lethargic or less active than usual")
    minutes_after_meal: float | None = Field(
        default=None, ge=0, description="Minutes between the last meal and the vomiting, if the user said")


class AppetiteDetails(Details):
    status: Literal["not_eating", "eating_less", "normal"] | None = Field(
        default=None, description="not_eating, eating_less or normal")
    hours_since_food: float | None = Field(
        default=None, ge=0, le=87600, description="Hours since the cat last ate normally, if known")


DETAIL_MODELS: dict[str, type[Details]] = {"vomit": VomitDetails, "appetite": AppetiteDetails}
"""Event types the conversation supports, with their validated detail shape."""

SUPPORTED_EVENT_TYPES: tuple[str, ...] = tuple(DETAIL_MODELS)


def validate_details(event_type: str, details: dict) -> dict:
    """Validate and normalise the details for an event type.

    Raises `KeyError` for an unsupported event type and `pydantic.ValidationError`
    for bad values. Returns a plain dict with every known field present (None when unknown).
    """
    return DETAIL_MODELS[event_type].model_validate(details).model_dump()


def describe_fields(event_type: str) -> str:
    """One line per field, for tool descriptions read by a language model."""
    model = DETAIL_MODELS[event_type]
    return "\n".join(f"- {name}: {field.description}" for name, field in model.model_fields.items())
