
---
name: job-intake
description: |
  Collects job description or vacancy details. 
  Only activated AFTER profile-intake and pii-check are completed.
version: 1.1.0
---

# Skill: Job Intake
## When to use
- Automated transition after Profile `pii-check` is finished.
- System state: `WAITING_FOR_JOB`.

## Workflow
1. **Prompt for Job**: Ask user to provide the vacancy text.
2. **Secure Isolation**: Wrap input in `[[NONCE_TAG]]`.
3. **PII Scan**: Automatically run `pii-check` on the raw text; classify and mask every flagged fragment before proceeding (see `pii-check` SKILL.md).
4. **HITL Choice**: Present the following options:
   - "(1) Add more job details"
   - "(2) Finished, proceed to MATCH"
5. **Persist**: If (2), save the final sanitized text to `data/job.json`. If (1), return to step 1 for the new text.

## Anti-patterns
- Do NOT use user profile data in this context.

