# JobMirror — Roadmap

This roadmap covers the final stage of the project — implementation on Google ADK.

The project went through two prototypes before this: the first established the logic, skills, and architecture; the second rewrote them without the data structuring module, which turned out to be the bottleneck. Each rewrite was fast because the logic stayed the same — only the code changed. Prototype history and plans are in `docs/prototypes_roadmap.md`.

***

**1. ADK Migration**

* All 7 skills on ADK: profile-intake, job-intake, match, post-match (all 3 options: gap-closing, discussion, cv-generation)
* discussion and cv-generation implemented for the first time (previously existed only as SKILL.md, not in code)
* No direct openai-client calls remain in the active path, except scan\_for\_pii and semantic\_check\_is\_command (shared internal utilities, not separate skills — kept as-is intentionally)

**2. Logs and Tests**

* Reconcile `trajectory.log` with ADK tracing (duplicate or not)
* Rewrite tests for the new call signature (mocks currently on `h.client.chat.completions.create`)

**3. Verification**

* Reconcile `specs/architecture.md` with the new architecture
* Full manual cycle completed: profile-intake → PII → job-intake → PII → match → post-match (gap-closing → re-match, discussion Q\&A, CV with Vibe Diff → cv.md → farewell screen → exit)

**4. Documentation**

* Update `README.md` for ADK setup
* Collect `docs/` (action\_plan, discussion\_skill\_design, match\_logic, Idea, system prompt) — excluding `git comment.md`
* README must explicitly cover the capstone evaluation table (ADK ✓, MCP Server — not yet, Security features ✓, Deployability, Agent skills)

**5. Submission Folder Assembly**

* Final run → save to `data/` (profile.json, job.json, cv.md + copy trajectory.log)
* Check `.gitignore` (no `.env`, no raw PII)

**6. Submit Materials (outside code)**

* Video (5 min): problem → why agents → architecture → demo → how it was built
* Kaggle Writeup
