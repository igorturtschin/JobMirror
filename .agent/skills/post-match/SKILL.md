***

## name: post-match description: | Menu shown after a MATCH result. Lets the user close gaps by adding experience to the profile, ask a question via the discussion skill, or proceed to CV generation. Implements items 6, 8, 9 from Идея\_проекта.md. version: 1.1.0

# Skill: Post-Match Menu

## When to use

* Automatically triggered right after the `match` skill produces a result.
* Also re-triggered after a gap-closing loop finishes (new MATCH → menu again).

## Workflow

1. **Show MATCH result** to the user (Match Level + Strength/Gap/Bonus).

2. **Present menu**:

   * "(1) Add experience and improve your profile"
   * "(2) Ask a question \[coming soon]"
   * "(3) Proceed to CV"

### Option 1 — Add experience and improve your profile

1. Prompt the user to describe the additional experience.
2. Wrap the input in the session's `[[NONCE_TAG]]` (Pillar 5, same as profile-intake).
3. Run `pii-check` on the new text before it touches long-term memory.
4. Append the sanitized text to `data/profile.json` (Append-only).
5. Re-run `match` with the updated profile + existing job.
6. Return to step 1 of this skill (show new MATCH result, show menu again).

### Option 2 — Ask a question

1. Prompt the user for their question.
2. Hand off to the `discussion` skill, passing Profile memory, Job memory, and the latest MATCH result (if available).
3. `discussion` is read-only: it does not modify Profile/Job, does not re-run `match`, and does not call other skills or tools.
4. Display the answer returned by `discussion`.
5. Present the same menu again (the 3 options above).

### Option 3 — Proceed to CV

* Hand off to `cv-generation` (not yet implemented — stub for now).
* Display: "CV generation is coming soon."
* Present the same menu again (the 3 options above).

## Anti-patterns

* Do NOT append new experience to the profile without running `pii-check` first.
* Do NOT skip the nonce-wrap step for new input — all user-provided text follows the same isolation rule as initial profile-intake.
* Do NOT silently re-run MATCH without showing the result and menu again afterward.
* Do NOT let `discussion` modify Profile/Job memory or trigger other skills — it is read-only.
