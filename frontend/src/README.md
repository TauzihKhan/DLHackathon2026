# frontend/src

Frontend source code: pages, components, services, utilities, and styles.

## Integration Notes
- Role 3 API integration is available via:
  - `services/insightsApi.ts`
  - `lib/http.ts`
- Base URL can be configured with `VITE_API_BASE_URL` (or `window.__API_BASE_URL__` at runtime).
