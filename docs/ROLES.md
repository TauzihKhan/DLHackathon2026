
ROLE DELEGATION
🎯 Role 1 — The Brain Builder
(Backend + Learning Logic)
What they do:
Build the mastery / XP system


Implement decay logic


Detect weak topics


Compute whatever standout metric you choose (blind spots / decay risk)


In layman terms:
This person builds the “thinking engine” of the app.
They don’t touch UI.
 They don’t worry about design.
 They focus on making the intelligence real.
This is your most technical person.

🎨 Role 2 — The Experience Designer
(Frontend + UX)
What they do:
Build dashboard


Show mastery charts


Show weak topics


Show recommendations


Make it look clean and convincing


In layman terms:
This person makes the intelligence visible.
They translate numbers into something judges understand in 5 seconds.
This role is extremely important.
 Clarity wins hackathons.

🤖 Role 3 — The AI Explainer
(LLM + Narrative Layer)
What they do:
Take structured backend outputs


Convert into natural-language explanations


Generate targeted practice questions


Polish demo wording


In layman terms:
This person turns data into insight.
They don’t analyze raw quiz scores.
 They translate computed metrics into clear feedback.
Important: They should only work with structured signals from Role 1.

🗃️ Role 4 — The Data Organizer
(Database + Quiz Structure)
What they do:
Design question schema


Tag topics / subtopics


Store attempts properly


Ensure data consistency


In layman terms:
This person makes sure the system has clean memory.
If data structure is messy, AI becomes nonsense.
This role prevents chaos.

🎤 Role 5 — The Storyteller & Integrator
(Demo + Slide + Flow + Glue)
What they do:
Make sure frontend talks to backend


Prepare demo scenario


Craft pitch narrative


Create 3-minute explanation flow


Handle deployment


In layman terms:
This person ensures the whole thing feels intentional.
They see the big picture.
Without this person, the system may work technically but feel disjointed.

------------------------------------------------------------------------
Problem we are solving
Students interact with learning materials over time, but they lack:
a clear model of what they know and forget


evidence-based explanations of their weaknesses


actionable next steps that adapt as their behavior changes


Our system models a student’s evolving learning state and uses AI to turn this model into clear guidance and targeted actions.

1️⃣ How learning interaction data is structured and tracked over time
Learning structure
Each module is decomposed into:
Module → Topic → Sub-topic
All learning interactions are linked to sub-topics, which are the atomic unit of tracking.

Interaction data model
Each learning interaction (quiz question, assignment question, flashcard review) is stored as an event with:
learner ID


timestamp


topic / sub-topic


difficulty


correctness


response time


These events form a time-ordered interaction log per student.

Learning state (computed, evolving)
From the interaction log, the system maintains a learning state per sub-topic, including:
mastery score


confidence / stability


last interaction timestamp


The learning state updates:
when new events arrive


when inactivity causes decay


This satisfies the requirement to model learning over time, not as snapshots.

2️⃣ How the system helps students understand their learning
Internal vs external representation
Internally, the system uses mastery, confidence, and decay


Externally, progress is presented using an XP-based abstraction for clarity and motivation


XP is derived from performance but is not the core learning model.

Student-facing understanding
Students can see:
XP per module


mastery distribution across topics


identification of weak or decaying sub-topics


This answers: “Where am I doing well, and where am I at risk?”

3️⃣ How AI provides clear and explainable insights (standout feature slot)
This section is intentionally reserved for the system’s differentiated AI capability.
The AI layer will:
receive structured learning state and historical evidence


reason over patterns of difficulty, not just low scores


generate explanations and targeted practice grounded in computed data


This section will be implemented as the project’s core innovation and demo focus.

4️⃣ How the system drives improvement and action
Targeted practice
Based on identified weak or decaying sub-topics:
the system selects focus areas


difficulty is calibrated to current mastery


AI generates targeted practice questions



Spaced repetition
Flashcards are linked to sub-topics and learning state.
Review frequency adapts based on:
mastery level


confidence


time since last review


This ensures the system responds to inactivity and forgetting, not just correctness.

