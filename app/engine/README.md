# app/engine

Core learner-state logic, decay, policy, and explanation helpers.

## Current Modules
- `state_engine.py`
  - Applies incoming events to learner state and computes updated mastery/confidence/xp.
- `decay.py`
  - Inactivity decay and risk-score calculations.
- `policy.py`
  - Deterministic weak-topic prioritization and recommended action selection.
- `explain.py`
  - Deterministic explanation facts assembly for `/insights`.
- `repetition.py`
  - Spaced-repetition interval policy and due-review queue assembly for `/reviews/due`.
- `narrative.py`
  - Role 3 narrative generation layer for `/insights/narrative`:
    - Uses structured deterministic insight as source of truth.
    - Calls LLM when configured.
    - Falls back to deterministic narrative/questions when LLM is unavailable or fails.
