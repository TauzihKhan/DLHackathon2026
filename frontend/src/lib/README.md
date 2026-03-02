# frontend/src/lib

Shared frontend utilities and helper modules.

## Current Files
- `http.ts`
  - `resolveApiBaseUrl(...)`: resolves backend base URL from `VITE_API_BASE_URL`, `window.__API_BASE_URL__`, or default `http://127.0.0.1:8000`
  - `httpGetJson(...)`: common GET helper with timeout + HTTP error handling
