from __future__ import annotations

from app.store.demo_seed import DEMO_LEARNER_IDS, seed_demo_data_if_needed
from app.store.in_memory_store import store


def main() -> None:
    seeded_count = seed_demo_data_if_needed()
    print(f"Seeded learners: {seeded_count}")
    print("Preview:")

    for learner_id in DEMO_LEARNER_IDS[:5]:
        state = store.get(learner_id)
        if state is None:
            print(f"- {learner_id}: no state")
            continue
        print(
            f"- {learner_id}: XP {state.xp_total}, "
            f"subtopics {len(state.subtopics)}, "
            f"updated {state.updated_at.isoformat()}"
        )


if __name__ == "__main__":
    main()
