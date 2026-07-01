
---
name: pii-check
description: |
  Mandatory security gate for data sanitization. 
  Identifies potential PII and requires manual classification (1-6) from the user.
  Used to ensure no sensitive personal data enters the system's long-term memory.
version: 1.3.0
---

# Skill: PII Check
## Workflow
1. **Detection**: Use Gemini 2.5 Flash light to extract potential PII fragments.
2. **Classification (HITL)**: For every fragment, prompt the user with 6 options:
   - (1) First Name
   - (2) Last Name
   - (3) Address
   - (4) Phone
   - (5) Email
   - (6) Not PII (Keep as is)
3. **Replacement**: Replace classified items with specific placeholders: `[[NAME]]`, `[[SURNAME]]`, `[[ADDRESS]]`, `[[PHONE]]`, or `[[EMAIL]]`.
4. **Transition**: Once all fragments are processed, proceed to the Job Intake stage.

## Anti-patterns
- Do NOT automate the selection of the masking type.
- Do NOT skip fragments; every item must be explicitly classified by the user.
```
