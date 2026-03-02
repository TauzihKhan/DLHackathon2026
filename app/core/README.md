# app/core

Shared backend runtime setup (configuration and logging).

## Current Modules
- `config.py`
  - Environment-driven Role 3 runtime settings (`OPENAI_API_KEY`, model, timeout, temperature, output tokens, question count).
  - Provides `get_ai_settings()` used by narrative engine.
