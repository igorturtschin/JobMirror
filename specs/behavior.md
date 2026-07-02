# JobMirror Behavior Specification (BDD)

This document defines the system's global UX behavior and state-transition logic for JobMirror using Given/When/Then (Gherkin) syntax. The Orchestrator must strictly follow these scenarios.

---

## Scenario 1: Secure Session Initialization
**Given:** The agent is launched in a new session.
**When:** The system initializes the environment.
**Then:** The agent generates a random 8-character string (Nonce-tag).
**And:** (FOR DEMO PURPOSES ONLY) The agent informs the user: "Session secured with tag [[NONCE_TAG]]".
*Note: In production, this tag remains hidden from the user to prevent Data Escape attacks.*

## Scenario 2: Isolated Profile Intake
**Given:** The system is in the `WAITING_FOR_PROFILE` state.
**When:** The user submits their experience or CV text.
**Then:** The Harness wraps the input into markers: `<[[NONCE_TAG]]>...</[[NONCE_TAG]]>`.
**And:** The system saves 100% of the raw text into `data/profile.json` (Append-only).
**And:** The agent automatically triggers the `pii-check` skill to sanitize the input.

## Scenario 3: PII Validation & HITL Confirmation
**Given:** The `pii-check` skill identifies potential personal data (names, phones, etc.).
**When:** The agent lists the identified data fragments to the user.
**Then:** The agent shows ONLY the flagged fragment itself, without surrounding context, and PAUSES execution requesting classification (1–5, per `pii-check` SKILL.md).
**And:** The system only proceeds to the next state after explicit user classification of every fragment (Human-in-the-Loop) — this is a blocking gate, not advisory.
**And:** Stop-condition for `profile-intake` / `job-intake` is a comparison of entry count in `data/*.json` **before vs. after** the run (`_count_entries()`), not `os.path.exists(path)` — files are append-only and may already exist from prior sessions, so existence alone is not a valid completion signal.

## Scenario 4: Strategic Intent Verification (Hallucination Defense)
**Given:** The system has a cleaned Profile and a Job Description.
**When:** The user requests a "Match" or "CV Generation".
**Then:** The agent must provide a Plain-English Summary (Strategic Vibe Diff) of its plan.
**And:** The agent asks: "I will emphasize [X] and downplay [Y] to match this role. Do you approve this strategy?".
**And:** The agent executes the detailed analysis ONLY after receiving a "Yes" from the user.

## Scenario 5: Trajectory Logging for Audit
**Given:** The agent performs any action or tool call.
**Then:** The agent records its reasoning in `logs/trajectory.log` using the OpenTelemetry format:
   - **Thought:** [Internal reasoning for the step]
   - **Tool Call:** [The specific skill invoked]
   - **Observation:** [The result returned by the tool]

## Scenario 6: Policy Gate (Prompt Injection Defense)
**Given:** The agent is about to execute any tool call (save data, mask PII, run match, call CV-gen, etc.), OR the harness is about to send a freshly collected user message to an LLM agent for the first time in `profile-intake`, `job-intake`, or the `post-match` gap-closing loop.
**When:** The orchestrator prepares the call's arguments (tool-call path), or the harness has just collected raw text from the user (pre-LLM path).
**Then:** The content is checked against `policies.yaml` BEFORE execution / BEFORE being sent to the LLM:
   - **Deterministic rules** (Traffic Light): fast regex/pattern checks — e.g. block writing un-masked PII to `data/profile.json` (scoped to the `save_data` action only, so it does not fire on raw text collected before PII-check has run), block content that contains text resembling instructions directed at the agent (e.g. "ignore previous instructions", "system:", "you must now...") — this rule applies at both the pre-LLM and pre-persistence points.
   - **Semantic checks** (Intelligent Referee): for ambiguous cases, a lightweight model call (Gemini 2.5 Flash-Lite) classifies whether the content is data or an injected command — at both points.
**And:** If a deterministic rule fires → the action is blocked outright, logged, and the user is informed.
**And:** If a semantic check flags risk → the action is paused for explicit HITL approval before proceeding, with a blocking `input()` call that explicitly flushes stdout beforehand so multi-line user input isn't misrouted as the approve/reject answer.
**And:** Every gate decision (pass/block/HITL) is recorded in `logs/trajectory.log`.
**And:** `policy_gate` has two call sites: (1) an ADK `before_tool_callback` (`policy_gate_callback`) gating tool-call arguments — its signature uses `tool_context=`, not `context=`, a recurring source of regressions that must be verified against the actual ADK callback signature on every edit, not assumed from memory; (2) a direct in-script call (`policy_gate("raw_input", message)`) on the raw collected message, before it is handed to the LLM agent at all. The second call site exists because an LLM agent can refuse or otherwise react to an injection attempt in plain text without ever invoking a tool — in that case the tool-call callback is never reached, and without the pre-LLM check the deterministic/semantic checks would silently not run at all.

## Scenario 7: Post-Match Menu (Gap Closing)
**Given:** The `match` skill has produced a result (Match Level, Strength, Gap, Bonus).
**When:** The result is shown to the user.
**Then:** The agent presents three options:
   - "(1) Add experience and improve your profile"
   - "(2) Ask a question"
   - "(3) Proceed to CV"
**And:** If the user selects (1):
   - The new experience text is wrapped in the session's `[[NONCE_TAG]]`.
   - The `pii-check` skill runs on the new text before it is persisted.
   - The sanitized text is appended to `data/profile.json`.
   - `match` re-runs with the updated profile, and this scenario repeats from the top.
**And:** If the user selects (2): hands off to the `discussion` skill (read-only ADK `LlmAgent`, no tools, sees Profile + Job + latest MATCH). After the answer is shown, the agent returns directly to this same three-option menu — there is no intermediate "Ask another question / Return to menu" step; asking another question is simply selecting (2) again from the menu.
**And:** If the user selects (3): hands off to `cv-generation` (Strategic Vibe Diff → HITL approval → generation, per its own SKILL.md). On completion the agent shows a final screen and exits the process; on "Revise" it returns to the Vibe Diff step.
**And:** All three menu options are reachable from the same post-match menu at every iteration — the menu is not reduced or altered between passes.

## Scenario 8: Input Mode Detection (Multi-line vs. Single-line)
**Given:** The harness must decide whether to collect the next user input as a single line (Enter) or multi-line (until `DONE`).
**When:** The agent has just produced a response.
**Then:** The harness inspects the **last agent response**: if it contains a numbered menu pattern (`_looks_like_menu_question()`, e.g. `(1)`/`(2)`), the next input is single-line; otherwise it is multi-line until `DONE`.
**And:** This applies uniformly to `profile-intake`, `job-intake`, and the `post-match` gap-closing loop — a fixed rule ("only the first turn is multi-line") is insufficient, since users may return to paste another multi-line block after a menu.
