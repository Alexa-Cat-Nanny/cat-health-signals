# cat-health-signals

Deterministic follow-up questions, patterns and red flags from a cat's health log.

Give it a list of timestamped events (vomiting, appetite, litter box, energy, weight,
meals, medication, food changes) and a cat profile. It tells you:

- **follow_up** – the one missing detail worth asking about next ("Was it food, hairball, or liquid?")
- **red_flags** – situations where a vet should be contacted, at three levels: `emergency`, `vet_today`, `mention_next_visit`
- **patterns** – what changed in the history, worded as observations, never as causes
- **summary** – a day-by-day timeline and period-over-period counts for a vet visit

It is pure Python: no I/O, no clock, no LLM. The same input always gives the same
output, so every rule is unit-tested. It was built for
[Cat Nanny](https://github.com/Alexa-Cat-Nanny/cat-nanny), an Alexa+ add-on, and can be used by any pet app.

> **Not veterinary advice.** This library organises observations so they can be shared
> with a vet. It does not diagnose. Red-flag conditions must be reviewed by a veterinarian
> before use.

## Install

```bash
pip install "cat-health-signals @ git+https://github.com/Alexa-Cat-Nanny/cat-health-signals.git"
```

## Use

```python
from datetime import datetime, UTC
from cat_health_signals import CatProfile, Event, assess

cat = CatProfile(cat_id="mochi", name="Mochi", sex="female")
event = Event(event_id="e1", cat_id="mochi", type="vomit",
              ts=datetime.now(UTC), details={"minutes_after_meal": 10})

result = assess(event, history=[event], cat=cat, now=datetime.now(UTC))
result.follow_up    # FollowUp(field='content', question='Was it food, hairball, or liquid?')
result.red_flags    # []
```

## Modules

| Module | What it decides |
|---|---|
| `models.py` | The data contract: `Event`, `CatProfile`, `FollowUp`, `Pattern`, `RedFlag`, `Assessment` |
| `followup.py` | Required details per event type and the question for each |
| `patterns.py` | Frequency change, meal timing, food change, weight trend |
| `redflags.py` | One function per rule, collected in `RULES` |
| `summary.py` | Timeline and totals for the vet summary |

## Status

Interfaces are stable; the rule tables are being filled in. Entries marked
`EXAMPLE ONLY` are placeholders for testing the pipeline.

## Develop

```bash
pip install -e ".[dev]"
pytest
```

## License

Apache-2.0
