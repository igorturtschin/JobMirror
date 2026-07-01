***

## name: cv-generation description: | Generates a tailored CV from the Profile, targeted at the current Job. Triggered from the post-match menu (option 3) after the user approves a Strategic Vibe Diff. Zero-fabrication: every claim must trace back to the verified Profile. version: 1.0.0

# Skill: CV Generation

## When to use

* Triggered from `post-match` menu, option "(3) Proceed to CV".
* Requires: Profile memory, Job memory, latest MATCH result.

## Workflow

1. **Strategic Vibe Diff (HITL gate)**

   * Based on Profile + Job + MATCH result, produce a short Plain-English summary: "I will emphasize \[X] and downplay \[Y] to match this role."
   * Ask the user: "Do you approve this strategy?"
   * Do NOT proceed to generation without explicit "Yes".
   * If the user says no / wants changes → revise the Vibe Diff, ask again.

2. **Generation**

   * Build the CV using ONLY facts present in Profile memory.
   * Structure: Summary, Experience, Skills (order may adapt to the emphasis approved in step 1, but no content may be invented).
   * Every bullet must be traceable to a specific Profile entry.

3. **Output**

   * Present the CV as plain text in the conversation.

4. **HITL Choice**

   * "(1) Looks good, finish"
   * "(2) Revise (go back to Strategic Vibe Diff)"

## Anti-patterns

* Do NOT generate the CV before the user approves the Strategic Vibe Diff.
* Do NOT invent experience, skills, or claims not present in Profile.
* Do NOT modify Profile or Job memory.
* Do NOT skip back to the Vibe Diff silently — always show it and wait for approval.
