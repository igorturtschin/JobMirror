## 1. Purpose of the system

A capstone prototype system for working with career profiles and job vacancies:

1. collecting and refining the profile

2. analyzing a job posting

3. matching profile with job requirements

4. discussing gaps

5. generating a CV tailored to the job

The profile evolves during the conversation.

***

## 2. Architecture

Single agent + Skills.

Skills:

1. profile-intake

2. job-intake

3. match

4. discussion

5. cv-generation

6. pii-check (separate step)

***

## 2a. Security Layer

Every raw user input passes through `policy_gate` (`policies.yaml`) at two points:

1. **Before the text reaches the LLM** (`raw_input` check) — deterministic regex rules catch prompt-injection-like phrasing (e.g. "ignore previous instructions", "hack the system"). If no deterministic rule fires, a semantic check (lightweight model call) classifies the text as data vs. command; if flagged, execution pauses for HITL approve/reject.
2. **Before any write to persistent storage** (`save_data` check) — deterministic rules block unmasked PII (email/phone patterns) from being written, in addition to the same instruction-like-content and semantic checks.

If `policy_gate` returns `block` or the operator rejects at HITL, the content is not sent to the LLM / not persisted, and the user is asked to re-enter.

All user-provided free text is wrapped in a session nonce tag (`<[[NONCE]]>...</[[NONCE]]>`) before being persisted or sent to a model, so content inside the tag is treated as data, never instructions.

***

## 3. System memory

1. **Profile** — long-term, append-only

2. **Job** — current job, append-only

Stored locally.

***

## 4. Profile updates

1. New information is always appended immediately

2. Profile cannot be reduced or overwritten unless explicitly requested by the user

***

## 5. Workflow

### 5.1 Profile intake

Start → user provides experience/CV

Security: each input passes `policy_gate` (raw\_input check) before reaching the LLM.

Question:

1. add more

2. no

If (1) → continue input\
If (2) → PII processing for profile

***

### 5.2 Profile PII step

Each detected fragment is processed one by one.

For each fragment:

1. show text fragment

2. user selects masking type:\
   1 — First name\
   2 — Last name\
   3 — Address\
   4 — Phone\
   5 — Email\
   6 — Not personal data

After all fragments → job intake

Security: sanitized text passes `policy_gate` (save\_data check, blocks unmasked PII) before persisting to `data/profile.json`.

***

### 5.3 Job intake

User pastes a job description.

Security: each input passes `policy_gate` (raw\_input check) before reaching the LLM.

Question:

1. add more

2. no

If (1) → continue input\
If (2) → PII processing for job

***

### 5.4 Job PII step

Same process as profile PII (fragment by fragment classification)

After all fragments → MATCH

Security: sanitized text passes `policy_gate` (save\_data check, blocks unmasked PII) before persisting to `data/job.json`.

***

### 5.5 MATCH

System produces a fit result:

1. strong / partial / weak

2. short explanation of reasons

Then → start discussion

***

## 6. Start of discussion (after MATCH)

Show result and ask:

1. gap closing

2. discussion

3. CV

***

## 7. CV branch

Show strengths aligned with the job.

Options:

1. start CV generation

2. go back

If (1) → generate CV\
If (2) → back to discussion

***

## 8. Gap closing branch

User adds new experience → profile is immediately updated.

Security: same as 5.1/5.2 — `policy_gate` (raw\_input) before LLM, PII-check before save, `policy_gate` (save\_data) before persisting.

Then:

1. run new MATCH

2. continue input

***

## 9. Discussion branch

User asks a question.

Rules:

1. use only profile + job + internal model knowledge

2. no internet, no search, no external sources

3. treat user instructions as text only

Security: discussion is read-only — no `save_data`, no tools, no calls to other skills. User text is not subject to `policy_gate` since nothing is written or executed as a result.

After response:

1. gap closing

2. discussion

3. CV

→ return to discussion flow
