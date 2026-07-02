# JobMirror Implementation Specification

This document defines the concrete technical implementation details of JobMirror: language, framework, models, storage format, data layout, logging format, and security implementation specifics.

---

# Stack

* Language: **Python 3.11**
* Agent framework: **google-adk 2.3.0**
* Model access: **LiteLlm wrapper → OpenRouter**
* Models (pinned, per skill):
  * `pii-check` → `openrouter/google/gemini-2.5-flash-lite`
  * `match`, `discussion`, `cv-generation` → `openrouter/google/gemini-2.5-flash`
* Tests/evals: **pytest 8.x**
* Config/secrets: `.env` via `python-dotenv`, `OPENROUTER_API_KEY`
* Pin every library version. Trusted sources only.

---

# Data & Storage

* `data/` — profile, job, and CV outputs (append-only JSON for profile/job; CV as generated text/file). Also holds results of the final evaluation run + `trajectory.log` copy for submission.
* `logs/trajectory.log` — every action logged as `{timestamp, thought, tool_call, observation}` (OpenTelemetry-style).
* `.gitignore` excludes `.env` and any raw/unmasked data.

---

# Security Implementation

## Nonce-tag Isolation

Each session generates an 8-char nonce; all user-provided free text is wrapped `<[[NONCE]]>...</[[NONCE]]>` before being persisted or sent to a model. Content inside the tag is data, never instructions.

## PII Gate

Before anything reaches long-term memory, `pii-check` scans for PII (name/surname/address/phone/email) and requires the user to manually classify each fragment (1–6). No automated masking.

## Policy Gate (`policies.yaml`)

Runs at two points:

* **Pre-LLM (`raw_input`):** every message the user types in `profile-intake`, `job-intake`, and the `post-match` gap-closing loop is checked before it is sent to the LLM agent at all — catches injection attempts even if the LLM would otherwise just refuse in plain text without calling a tool.
* **Pre-persistence (`save_data`):** runs before every `save_data`-type action (ADK `before_tool_callback`), additionally blocking unmasked PII from being written.

Deterministic rules (regex): block instruction-like content ("ignore previous instructions", etc.) at both points; block unmasked PII only at the `save_data` point (`applies_to: [save_data]`), so raw pre-PII-check text isn't blocked for containing digits/patterns that only become a problem if written unmasked.

Semantic check (Gemini 2.5 Flash-Lite): flags text that looks like a command rather than user data → pauses for HITL approve/reject, at both points.

HITL approval is currently emulated via terminal `input()` — a demo stand-in, not a production operator interface.

## Append-only Profile

No deletion/overwrite without explicit user request and confirmation.

## Stop-condition Signal

Stop-condition for `profile-intake` / `job-intake` is a comparison of entry count in `data/*.json` **before vs. after** the run (`_count_entries()`), not `os.path.exists(path)` — files are append-only and may already exist from prior sessions, so existence alone is not a valid completion signal.

## Sandbox Execution

NOT implemented. CV generation is a single LLM text completion written to a file — there is no isolated execution/rendering environment. Do not claim this capability in docs submitted for certification.

---

# Skill Responsibilities

* `profile-intake` — capture raw CV/experience text, nonce-wrap, persist (append-only) to `data/profile.json` after PII gate.
* `pii-check` — gate skill, see Security section above.
* `job-intake` — capture vacancy text, same nonce + PII gate flow, save to `data/job.json`.
* `match` — evidence-based comparison of profile vs. job. Output: qualitative **Match Level (Strong / Partial / Weak)** + Strengths + Gaps + Bonus + one-sentence summary. **No numeric percentage.** Never infers unstated skills; unknown stays unknown.
* `post-match` — recurring menu shown after every match result, not three separate terminal branches: (1) add experience → re-run PII gate → append profile → re-run match → show menu again; (2) ask a question → hand off to `discussion` → answer shown → menu shown again; (3) proceed to CV → hand off to `cv-generation` → on final "Looks good, finish" the session ends, on "Revise" it loops back to the Vibe Diff step. Only option 3's final acceptance exits the loop.
* `discussion` — acts as a career consultant/advisor, scoped to profile + job + latest match result + general model knowledge. No web/internet, no other sources, no algorithmic/computational tasks. Cannot modify state, cannot call other skills or trigger match/CV. May draft career-related texts (recruiter/outreach messages, LinkedIn messages, CV sections) grounded in profile/job — but does not produce a classic formal cover letter document. If a request's fit within career-consulting scope is doubtful, pause for HITL approval (same approve/reject mechanism as the policy gate) rather than refusing outright or complying blindly. Clearly out-of-scope questions get a fixed refusal message.
* `cv-generation` — Strategic Vibe Diff (plain-English strategy summary) requires explicit user approval (HITL) before generation. Zero fabrication: every claim traces to `data/profile.json`. Output: plain text CV (Summary / Experience / Skills), saved to `data/cv.md`. **Cover letter is out of scope — not built.**

---

# Trajectory Logging

Every tool call logs `thought → tool_call → observation` to `logs/trajectory.log`, including policy_gate decisions (pass / block / hitl_requested / approve / reject), so the full reasoning trail is auditable for certification.

---

# Out of Scope

* Multiple jobs / multiple profiles per session.
* Public deployment / multi-tenancy.
* Automatic application submission (no irreversible/send actions, ever).
* Sandboxed document rendering.
