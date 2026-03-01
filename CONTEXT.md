# Project Context: DLHackathon2026

## Mission
Build and demo a working hackathon project by the deadline with clear ownership, fast iteration loops, and a stable demo path.

## Non-Goals
- Perfect architecture for long-term scale
- Premature optimization
- Building optional features before core demo flow works

## Deadline and Scope
- Event: Hackathon 2026
- Working model: prioritize a thin, end-to-end vertical slice first, then iterate.

## Team Working Model
- Keep PRs/slices small and merge often.
- Prefer "working and visible" over "theoretically ideal."
- Every significant change should update this file if assumptions change.

## Current Repo State
- Backend-first scaffold is set and documented in `docs/PROJECT_STRUCTURE.md`.
- FastAPI-oriented module boundaries are chosen to optimize speed-to-demo.

## Proposed Baseline Architecture
- `app/`: API, domain logic, services, DB, jobs, evaluation, and tests
- `scripts/`: seed/replay/dev helpers
- `data/`: demo fixtures
- `docs/`: product and technical references

Reference structure and ownership rules:
- `docs/PROJECT_STRUCTURE.md`

## Environment Setup (To Update As You Decide Stack)
- Install dependencies
- Run app locally
- Run tests/lint

Add concrete commands here once stack is finalized.

## Coding Conventions
- Keep functions/modules small and testable.
- Use clear names over clever abstractions.
- Add comments only where intent is non-obvious.
- Avoid broad refactors during hackathon unless blocking progress.

## Definition of Done (Hackathon)
- Feature is demoable end-to-end.
- Basic error handling exists for key paths.
- Minimal documentation updated (`README.md` + this file).
- Another teammate can run it locally.

## API and Data Contracts
Document API endpoints and payload shapes here once defined.

Template:
- Endpoint:
- Method:
- Request:
- Response:
- Error cases:

## Open Questions
- What is the exact demo narrative?
- What are must-have vs nice-to-have features?
- What should be mocked vs fully implemented?

## Known Risks
- Scope creep under time pressure
- Late integration surprises
- Environment drift across teammates

## Daily Operating Checklist
- Confirm top 1-2 priorities for next session.
- Ensure main/demo branch is runnable.
- Capture new decisions in this file.
