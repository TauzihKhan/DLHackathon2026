from datetime import datetime

DECAY_HALF_LIFE_DAYS = 14.0
MAX_DECAY_PENALTY = 0.35

"""
 - 1 day inactivity: lower risk, higher retained mastery.
  - 30 days inactivity: higher risk, lower retained mastery.
  - Confirms monotonic behavior and valid ranges.
"""


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def days_since(last_interaction_at: datetime, now: datetime) -> float:
    """Return non-negative elapsed days between two timestamps."""

    delta_seconds = (now - last_interaction_at).total_seconds()
    return max(0.0, delta_seconds / 86400.0)


def compute_decay_risk_score(last_interaction_at: datetime, now: datetime) -> float:
    """Map inactivity duration to decay risk in [0, 1]."""

    inactivity_days = days_since(last_interaction_at, now)
    risk = 1.0 - (2.0 ** (-inactivity_days / DECAY_HALF_LIFE_DAYS))
    return _clamp_01(risk)


def apply_decay_to_mastery(
    mastery: float,
    last_interaction_at: datetime,
    now: datetime,
) -> float:
    """Reduce mastery based on inactivity while keeping output in [0, 1]."""

    safe_mastery = _clamp_01(mastery)
    risk = compute_decay_risk_score(last_interaction_at, now)
    decayed_mastery = safe_mastery * (1.0 - (MAX_DECAY_PENALTY * risk))
    return _clamp_01(decayed_mastery)
