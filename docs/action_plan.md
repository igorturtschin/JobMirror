Approximate schedule (excluding presentation):

1. **Design and Specifications (Day 1 / ~4–6 hours):**

   * Writing detailed BDD scenarios (Given/When/Then) for each skill in `/specs`.
   * Creating `AGENTS.md` with general safety rules and the project's engineering “DNA”.

2. **Orchestrator and Skills Implementation (Day 2 / ~6–8 hours):**

   * Creating the base agent and folder structure for skills.
   * Coding the skills themselves (PII-checker, CV-gen) using your AI assistants.

3. **Security and Testing (Day 3 / ~6–8 hours):**

   * Implementing data tags, sandboxing, and PII logic.
   * Writing **Evals** (at least 3 cases per skill) to verify trajectories.
   * Checking convergence — how many steps the agent needs to complete a task.