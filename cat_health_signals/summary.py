"""Vet summary: a day-by-day timeline plus totals, computed from the history. No judgement, only counting."""

from __future__ import annotations

from datetime import date, datetime, timedelta, tzinfo

from pydantic import BaseModel, Field

from .models import CatProfile, Event

SYMPTOM_TYPES = ("vomit", "appetite", "litter", "energy")
MARKER_TYPES = ("vomit", "appetite", "litter", "energy", "food_change", "vet_visit", "medication")


class DayCell(BaseModel):
    day: date
    counts: dict[str, int] = Field(default_factory=dict)
    """Event type -> number of events that day (only types in MARKER_TYPES)."""


class PeriodComparison(BaseModel):
    event_type: str
    current: int
    previous: int


class WeightChange(BaseModel):
    first_kg: float
    last_kg: float
    change_pct: float


class VetSummaryData(BaseModel):
    cat_name: str
    days: int
    start: date
    end: date
    timeline: list[DayCell]
    comparisons: list[PeriodComparison]
    weight: WeightChange | None = None
    food_changes: list[dict] = Field(default_factory=list)


def build_summary(history: list[Event], cat: CatProfile, now: datetime, days: int = 30, tz: tzinfo | None = None) -> VetSummaryData:
    """Summarise the last `days` days; `history` should cover 2x`days` so the previous period can be compared."""
    tz = tz or now.tzinfo
    local_now = now.astimezone(tz) if tz else now
    end = local_now.date()
    start = end - timedelta(days=days - 1)
    period_start = now - timedelta(days=days)
    prev_start = now - timedelta(days=2 * days)

    cells = {start + timedelta(days=i): DayCell(day=start + timedelta(days=i)) for i in range(days)}
    for e in history:
        d = (e.ts.astimezone(tz) if tz else e.ts).date()
        if d in cells and e.type in MARKER_TYPES:
            cells[d].counts[e.type] = cells[d].counts.get(e.type, 0) + 1

    comparisons = []
    for t in SYMPTOM_TYPES:
        cur = sum(1 for e in history if e.type == t and period_start < e.ts <= now)
        prev = sum(1 for e in history if e.type == t and prev_start < e.ts <= period_start)
        if cur or prev:
            comparisons.append(PeriodComparison(event_type=t, current=cur, previous=prev))

    weights = sorted(
        (e for e in history if e.type == "weight" and period_start < e.ts <= now and isinstance(e.details.get("kg"), int | float)),
        key=lambda e: e.ts,
    )
    weight = None
    if len(weights) >= 2:
        first, last = float(weights[0].details["kg"]), float(weights[-1].details["kg"])
        weight = WeightChange(first_kg=first, last_kg=last, change_pct=round((last - first) / first * 100, 1))

    food_changes = [
        {"date": e.ts.date().isoformat(), "from": e.details.get("from"), "to": e.details.get("to")}
        for e in history
        if e.type == "food_change" and period_start < e.ts <= now
    ]

    return VetSummaryData(
        cat_name=cat.name,
        days=days,
        start=start,
        end=end,
        timeline=[cells[d] for d in sorted(cells)],
        comparisons=comparisons,
        weight=weight,
        food_changes=food_changes,
    )
