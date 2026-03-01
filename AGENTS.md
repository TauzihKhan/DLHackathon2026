# Agent Instructions for This Repo

## Primary Context Source
Before making changes, read:
1. `README.md`
2. `CONTEXT.md`

If there is a conflict, prefer:
1. explicit user instructions in the current task
2. `CONTEXT.md`
3. `README.md`

## Collaboration Rules
- Optimize for speed-to-demo and end-to-end functionality.
- Keep changes focused and minimal.
- Do not make broad speculative refactors.
- Document assumptions in `CONTEXT.md` when they affect team decisions.

## Expected Workflow
- Confirm task and identify impacted files.
- Implement smallest viable change.
- Run any relevant checks/tests available.
- Report what changed and any follow-up actions.

## Documentation Hygiene
When introducing a new feature or workflow, update:
- `README.md` for usage/setup
- `CONTEXT.md` for product/technical decisions

## Safe Defaults During Hackathon
- Prefer explicit, readable code.
- Add only essential tests/checks for critical flows.
- Flag blockers early with concrete options.

