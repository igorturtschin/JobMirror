# JobMirror — Action Plans (Prototypes)

This file contains the action plans for the first and second prototypes. Repository links: https://github.com/igorturtschin/jobmirror-proto-1 https://github.com/igorturtschin/jobmirror-proto-2

The final project plan is in `docs/roadmap.md`.

***

## Prototype 1 — Action Plan v1

> Course principle: specification first, then code. Code is disposable. This is a sequence of actions: step → what we do → what comes out. Skills are created ONCE — at step 13.

***

### Stage A. Understanding and Decisions

#### Step 1. Write out all the logic in plain words (for yourself)

**Do:** describe the entire end-to-end flow in plain text: profile → job analysis → comparison → discussion → confirmed profile update → document generation. Define what counts as memory, what is case state, the core rule "new facts are not written to the profile immediately", the main product principle "detailed profile = core value", buttonless UX flow, status line as a loop, language policy, reset, session restore. **Output:** `MVP_V1_Documentation.md`. No code. Do not create parallel documents with the same logic.

#### Step 2. Lock in architectural decisions

**Do:** based on step 1, make and record decisions: (1) single agent

* Skills library, not multi-agent; (2) no MCP in MVP; (3) profile and cases stored in a local file; (4) source of truth — specs + skills; (5) session structure — explicit UX flow, not LLM routing. **Output:** a short list of decisions (will go into AGENTS.md at step 4).

***

### Stage B. Skeleton and Shared Documents

#### Step 3. Create an empty repository skeleton

**Do:** structure only, no content: `specs/`, `.agent/skills/`, `storage/`, `evals/`, `notes/`. Empty `AGENTS.md` and `specs/copy.md`. **Output:** folder tree and empty files. (Skills are written at step 13.)

#### Step 4. Write AGENTS.md

**Do:** project DNA: name (JobMirror), stack + versions, architecture, hard rules (new facts → `pending_facts`; no irreversible actions; untrusted input; no fabrication; expand-only; sandbox; reset passphrase), language policy, UX rules (status line, section numbering, diff-preview, file naming), workflow rules (evals before code), Skills catalog, main product principle. **Output:** `AGENTS.md`.

#### Step 5. Write shared conventions

**Do:** cross-cutting decisions so specs don't diverge: storage format and path, level taxonomy (role / skill), deduplication rule, output document formats, file naming convention. **Output:** `specs/_conventions.md`.

#### Step 6. Write agent copy (reply texts)

**Do:** all agent phrasing in one file (greeting, intake-tail, job input with single-vacancy warning, match, discussion-tail, post-update, document selection, diff-preview, reset, garbage input, restore). Template for each reply: "question → why this matters → next step". **Output:** `specs/copy.md`.

***

### Stage C. Specifications (Source of Truth, Before Code)

#### Step 7. Data specs (entities)

**Do:** data structures: profile and job model. **Output:** `specs/profile.md`, `specs/job_model.md`.

#### Step 8. Behavior specs (what each block does)

**Do:** BDD/Gherkin for each logic block. **Output:** `specs/profile-intake.md`, `specs/job_discussion.md`, `specs/match_logic.md`, `specs/profile_update.md`, `specs/application.md`.

#### Step 9. Human spec review (checkpoint)

**Do:** read through all specs, fix logic and contradictions. No code. **Output:** approved specs. Logic errors are caught here.

***

### Stage D. Preparation for Implementation

#### Step 10. Derive the skills list from specs

**Do:** from specs, compile the final skills catalog with router descriptions (what it does / when / when NOT). Fill the catalog in AGENTS.md. **Output:** list: `profile-intake`, `job-analysis`, `match-logic`, `job-discussion`, `profile-update`, `application-generation`.

#### Step 11. Set up storage and access tool

**Do:** local storage (profile + job case, including discussion log and `match_stale` field) and access tool. No MCP. No hardcoded strings. **Output:** working storage layer + tool.

#### Step 12. Prepare eval harness

**Do:** decide where eval cases live (`evals/`), how to run them, threshold (trigger ≥ 90%). **Output:** empty but working eval runner.

***

### Stage E. Skills Implementation

#### Step 13. Implement skills one by one, in pipeline order

Order: `profile-intake` → `job-analysis` → `match-logic` → `job-discussion` → `profile-update` → `application-generation`. For EACH skill, repeat:

* **13a.** Run the task manually without the skill — see where the agent breaks.
* **13b.** Write 3 eval cases (2 positive, 1 negative) — BEFORE the body.
* **13c.** Write the `SKILL.md` body (+ `scripts/`, `references/` if needed). All reply texts are taken FROM `specs/copy.md`, not hardcoded into the skill.
* **13d.** Run evals; if failing — fix; do not move forward. **Output:** library of working, tested skills.

#### Step 14. Implement the UX flow (session state machine)

**Do:** stitch steps into a loop with states (Profile → Job → Match → Discussion → Documents → ↺), status line, session restore, reset, handling garbage/empty input. This is code that calls skills and injects reply texts from `copy.md`. **Output:** working end-to-end dialogue.

***

### Stage F. Security and Observability

#### Step 15. Guardrails / sandbox

**Do:** sandbox for document generation; treat job/resume as untrusted input; block irreversible actions; pin versions; reset passphrase; diff-preview before document edits. **Output:** active protective checks.

#### Step 16. Observability

**Do:** log the trajectory (which skills fired, tool calls, tokens/latency). The user discussion log is a separate thing — it is part of the product (see step 11). **Output:** service logs for debugging and evals.

***

### Stage G. Evaluation and Iteration

#### Step 17. System eval of the full dialogue

**Do:** evaluate the end-to-end scenario: session-prefix as intent rubric, intent satisfaction / correctness / trajectory, success = convergence to the right CV in few edits. **Output:** end-to-end quality report.

#### Step 18. Collect corrections and iterate

**Do:** every "no, that's wrong" = a labeled failure; cluster → prioritize → return to steps 13–17. **Output:** list of fixes and the next iteration.

#### Step 19. Review-skill in CI and docs sync

**Do:** code-review skill on changes; keep README/CHANGELOG in sync with specs and code; reply texts are only edited in `specs/copy.md`. **Output:** sustainable maintenance loop.

***

### Quick Reference (Prototype 1)

1 logic in words (MVP doc) → 2 decisions → 3 skeleton → 4 AGENTS.md → 5 conventions → 6 copy.md → 7 data specs → 8 behavior specs → 9 spec review → 10 skills list → 11 storage → 12 eval harness → 13 skills one by one (eval→body→run) → 14 UX flow (state machine) → 15 guardrails/sandbox → 16 observability → 17 system eval → 18 iteration → 19 CI/docs.

***

## Prototype 2 — Action Plan v2

### 1. Design and Specifications

* Verify compatibility of detailed BDD scenarios from Prototype 1 (Given/When/Then) for each skill in `/specs`.
* Update `AGENTS.md` from Prototype 1 with general security rules and the project's engineering DNA.

### 2. Orchestrator and Skills Implementation

* Create the base agent and folder structure for skills.
* Rewrite skills (PII-checker, CV-gen) from Prototype 1 using AI assistants.

### 3. Security and Testing

* Implement data tags and PII logic.
* Write **Evals** (at least 3 cases per skill) to verify trajectories.
* Check convergence — how many steps the agent needs to complete a task.
