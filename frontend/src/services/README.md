# frontend/src/services

API clients and service-layer logic for backend communication.

## Current Files
- `insightsApi.ts`
  - `getStudentInsights(learnerId)`: calls `GET /students/{id}/insights`
  - `getStudentNarrativeInsights(learnerId)`: calls `GET /students/{id}/insights/narrative`
- `reviewsApi.ts`
  - `getDueReviews(learnerId)`: calls `GET /students/{id}/reviews/due`
