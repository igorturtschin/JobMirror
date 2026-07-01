# JobMirror Architecture Specification

This document defines the architecture of JobMirror: system principles, component boundaries, the state machine, and the concrete behavioral contract (BDD scenarios) the Orchestrator must follow.

---

# Purpose

JobMirror assists users in tailoring their professional profile and CV for a target job while maintaining security, auditability, and human control over important decisions.

---

# Core Principles

The system SHALL satisfy the following principles at all times.

## Data Integrity

- Raw user input is immutable.
- User data is never silently modified.
- Persistent records are append-only.
- Existing records are never overwritten or deleted.
- Every derived artifact can be traced back to its original input.

## Human-in-the-Loop (HITL)

The user remains the final decision-maker.

The system SHALL require explicit user approval before:

- strategic profile positioning,
- CV generation,
- any ambiguous security decision,
- any action requiring human classification.

## Security

The system SHALL treat all user input as untrusted.

Every action that may affect stored data or invoke an external capability SHALL pass a security validation layer (`policy_gate`) before execution.

## Auditability

All significant actions SHALL be traceable.

The system SHALL maintain an audit trail of:

- state transitions,
- tool invocations,
- security decisions,
- generated artifacts.

## State Ownership

The orchestrator is the single authority responsible for workflow progression.

Individual skills or components SHALL NOT change workflow state directly.

Where a state transition depends on a measurable fact (e.g. "has new data been persisted"), the orchestrator MUST use a deterministic, verifiable signal — such as comparing entry counts before/after an action — rather than an ambiguous one. `os.path.exists(path)` is explicitly NOT a valid completion signal for append-only storage, since the file may already exist from a prior session.

## Separation of Responsibilities

The architecture separates responsibilities into four logical domains:

| Domain | Responsibility |
|---------|----------------|
| Orchestrator | Controls workflow and state transitions |
| Skills | Perform domain-specific tasks |
| Security Layer | Validates actions before execution |
| Persistence Layer | Stores immutable system records |

Each domain communicates only through well-defined interfaces.

---

# System State Machine

The system progresses through explicit states.

```
NEW_SESSION
        │
        ▼
WAITING_FOR_PROFILE
        │
        ▼
PII_REVIEW
        │
        ▼
WAITING_FOR_JOB
        │
        ▼
READY_FOR_MATCH
        │
        ▼
MATCH_COMPLETE
        │
        ▼
POST_MATCH_MENU ◄─────────────┐
      │      │      │                    │
      │      │      └─(3) CV──► CV_GENERATION ─► FINISHED
      │      └─(2) Discussion ─► answer ──┘
      └─(1) Gap-closing ─► re-run MATCH ──┘
```

The post-match menu (options 1/2/3) is a single recurring state, not three
independent terminal branches: after option 1 (gap-closing) or option 2
(discussion), control returns to the same menu. Only option 3
(CV generation, on "Looks good, finish") exits to `FINISHED`.

At any moment the system SHALL exist in exactly one state.

---

# Workflow

## Session Initialization

When a new session begins: create an isolated session context, establish session identity, initialize audit logging.

## Profile Intake

The system accepts the user's professional profile. The original content becomes the authoritative source for all future processing. No transformation may replace or modify the original submission.

## Sensitive Data Review (PII Gate)

The PII gate is a **mandatory, blocking control mechanism** — not merely informational. Potential personal information is identified, and execution pauses until the user provides explicit classification for every fragment. No downstream processing may continue before review is complete.

## Job Intake

The system receives the target job description. The job description becomes immutable input for subsequent analysis.

## Strategy Review

Before performing matching or CV generation, the system explains its intended strategy in clear, non-technical language. The user must explicitly approve this strategy before execution continues.

## Matching

The system compares the approved profile against the target job. The output identifies strengths, gaps, bonus skills, and overall Match Level.

## Post-Match Iteration

After presenting the match result, the system shows a single recurring three-option menu: improve the profile, ask a question, or generate a CV. Selecting option 1 or 2 returns control to this same menu after completing the action; only option 3 (on final CV acceptance) exits the loop.

## Discussion

Discussion is informational only. It may reference existing information but SHALL NOT modify persistent data.

## CV Generation

CV generation uses only approved inputs. Before generation begins, the strategy must be approved. The user may revise the strategy and repeat generation.

---

# Architectural Invariants

The following conditions SHALL always hold.

- **User Control:** No irreversible operation occurs without explicit user approval.
- **Data Preservation:** Original user input is never lost.
- **Deterministic State Progression:** Every transition occurs from a valid state to another valid state. Undefined transitions are prohibited.
- **Complete Traceability:** Every externally observable result can be traced through originating inputs, workflow state, and executed actions.

---

# Failure Principles

When an operation cannot be completed:

- existing data remains unchanged;
- partial results are not committed;
- the failure is recorded;
- the workflow remains in a valid state.

The system SHALL fail safely rather than continue in an undefined state.

---

# Out of Scope

This document intentionally does not define: programming language, storage format, APIs, or framework-specific (ADK) implementation details beyond what's needed to state the behavioral contract below. Those belong to the implementation specification.

---

# Behavioral Contract (BDD Scenarios)

The Orchestrator must strictly follow these scenarios.

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