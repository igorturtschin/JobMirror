# JobMirror ADK Specification

This document describes the ADK-specific implementation details for JobMirror: how skills are wired as ADK tools, callback signatures, and known ADK-specific pitfalls.

---

# ADK Migration Status

**ADK migration: DONE.** All 7 skills (`profile-intake`, `pii-check`, `job-intake`, `match`, `discussion`, `cv-generation`, `post-match` with all 3 options) run on Google ADK. No direct `openai`-client calls remain in the active skill path; the `openai` client is used only by two internal utilities (`scan_for_pii`, `semantic_check_is_command`) — shared helpers, not skills, left as-is intentionally.

---

# Architecture

**One agent with multiple skills.** Not multi-agent, not sub-agents. Skills are exposed to the single root agent as **tools**.

Skills: `profile-intake`, `pii-check` (gate), `job-intake`, `match`, `discussion`, `cv-generation`, `post-match` (menu/router after match).

---

# Policy Gate Integration

`policy_gate` has two call sites:

1. An ADK `before_tool_callback` (`policy_gate_callback`), gating tool-call arguments (e.g. `save_data`-type actions) before execution.
2. A direct in-script call on raw user input (`policy_gate("raw_input", message)`), run in the harness loop right after text is collected and before it is sent to the LLM at all — restored to close a gap where an LLM agent could simply refuse/react to an injection attempt in free text without ever calling a tool, leaving the deterministic/semantic checks unreached.

The `raw_input` action name deliberately does not match the PII-write rule (`applies_to: [save_data]`), so PII regex still only fires at the `save_data` call site, after PII-check has run — not on raw pre-PII text. Internal logic unchanged either way: deterministic regex rules run first, then semantic check (`gemini-2.5-flash-lite`) only if regex is inconclusive, then HITL pause on flag.

---

# Known ADK Pitfalls

## `before_tool_callback` Signature

The `policy_gate_callback` registered as ADK `before_tool_callback` uses `tool_context=` as the parameter name, **not** `context=`. This is a recurring source of regressions that must be verified against the actual ADK callback signature on every edit — never assume from memory.

## `discussion` Skill

`discussion` is a read-only ADK `LlmAgent` with **no tools**. It sees: Profile + Job + latest MATCH result. It cannot call other skills, cannot modify state, and cannot trigger match or CV generation.

## Input Mode Detection

The harness inspects the **last agent response** to decide single-line vs. multi-line input collection: if it contains a numbered menu pattern (`_looks_like_menu_question()`, e.g. `(1)`/`(2)`), the next input is single-line; otherwise multi-line until `DONE`. This applies uniformly across `profile-intake`, `job-intake`, and the `post-match` gap-closing loop — a fixed rule ("only the first turn is multi-line") is insufficient.
