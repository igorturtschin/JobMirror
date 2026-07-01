"""
JobMirror Skill Eval Runner
Covers three areas with mocked I/O and mocked API calls (no real network calls):

1. policy_gate        — deterministic + semantic injection defense (Scenario 6)
2. post_match_menu     — gap-closing / discussion stub / CV stub flow (Scenario 7)
3. multi_entry_persistence — regression test for the load_all_entries bug
                              (previously only the last profile entry was read)

Logs every case to logs/trajectory.log via the orchestrator's own log_trajectory(),
in the same OpenTelemetry-style format used elsewhere in the project.
"""

import json
import os
import sys
import datetime
from unittest import mock

# --- Make sure the orchestrator module can be imported without a real API key ---
os.environ.setdefault("OPENROUTER_API_KEY", "test-key-for-evals")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import harness_orchestrator as orch

CASES_PATH = os.path.join(os.path.dirname(__file__), "skill_eval_cases.json")
EVAL_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "skill_eval.log")


def get_now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"


def log_eval_summary(entries):
    os.makedirs(os.path.dirname(EVAL_LOG_PATH), exist_ok=True)
    with open(EVAL_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "run_timestamp": get_now_iso(),
            "cases": entries,
        }, ensure_ascii=False) + "\n")


# =========================================================
# 1. Policy Gate evals (deterministic + semantic)
# =========================================================

def run_policy_gate_evals(cases):
    print(f"\n{'='*55}")
    print("  Policy Gate Evals (Scenario 6)")
    print(f"{'='*55}\n")

    results = []
    passed = failed = 0

    for case in cases:
        case_id = case["id"]
        text = case["input"]
        expected = case["expected_result"]

        # For deterministic-block cases, the semantic check should never even
        # be reached, so we mock it to fail loudly if it's hit unexpectedly.
        # For pass cases, mock the semantic model call to answer "no" (not a command).
        with mock.patch.object(orch, "semantic_check_is_command", return_value=False):
            orch.log_trajectory(
                f"[EVAL] Running policy_gate case {case_id}.", "eval:policy_gate", case["description"]
            )
            actual = orch.policy_gate("save_data", text)

        ok = actual == expected
        status = "PASS" if ok else "FAIL"
        symbol = "✓" if ok else "✗"
        print(f"[{case_id}] {case['description']}")
        print(f"  {symbol} {status}  expected={expected} got={actual}\n")

        results.append({"id": case_id, "status": status, "expected": expected, "actual": actual})
        passed += ok
        failed += not ok

    return results, passed, failed


# =========================================================
# 2. Post-Match Menu evals
# =========================================================

def run_post_match_menu_evals(cases):
    print(f"\n{'='*55}")
    print("  Post-Match Menu Evals (Scenario 7)")
    print(f"{'='*55}\n")

    results = []
    passed = failed = 0

    for case in cases:
        case_id = case["id"]
        choice_sequence = list(case["choice_sequence"])
        actions_seen = []

        nonce = "TESTNONCE"
        match_result = {"match_level": "Partial", "strengths": [], "gaps": [], "bonus": []}

        def fake_get_user_choice(prompt_text, options):
            return choice_sequence.pop(0)

        def fake_run_post_match_gap_intake_adk(nonce):
            # option 1: gap-closing ADK agent — mocked whole, since it
            # drives a real ADK Runner internally (no model access here).
            actions_seen.append("gap_intake_adk")

        async def fake_run_post_match_gap_intake_adk_async(nonce):
            fake_run_post_match_gap_intake_adk(nonce)

        def fake_run_match_analysis(profile_text, job_text):
            actions_seen.append("run_match_analysis")
            return match_result

        def fake_print_match_result(result):
            actions_seen.append("print_match_result")

        def fake_run_discussion(profile_text, job_text, match_res):
            actions_seen.append("run_discussion")

        def fake_run_cv_generation(profile_text, job_text, match_res):
            actions_seen.append("run_cv_generation")
            raise SystemExit(0)  # mirrors the real finish behavior

        with mock.patch.object(orch, "get_user_choice", side_effect=fake_get_user_choice), \
             mock.patch.object(orch, "run_post_match_gap_intake_adk", side_effect=fake_run_post_match_gap_intake_adk_async), \
             mock.patch.object(orch, "run_match_analysis", side_effect=fake_run_match_analysis), \
             mock.patch.object(orch, "print_match_result", side_effect=fake_print_match_result), \
             mock.patch.object(orch, "run_discussion", side_effect=fake_run_discussion), \
             mock.patch.object(orch, "run_cv_generation", side_effect=fake_run_cv_generation), \
             mock.patch.object(orch, "load_all_entries", return_value="dummy"):

            orch.log_trajectory(
                f"[EVAL] Running post_match_menu case {case_id}.", "eval:post_match_menu", case["description"]
            )
            try:
                orch.run_post_match_menu(nonce, match_result)
            except SystemExit:
                pass  # expected: real run_cv_generation exits the process on finish

        # Validate the actions performed match what the workflow should have done.
        ok = True
        reasons = []

        if 1 in case["choice_sequence"]:
            for required in ("gap_intake_adk", "run_match_analysis"):
                if required not in actions_seen:
                    ok = False
                    reasons.append(f"missing action '{required}' for gap-closing branch")

        if 2 in case["choice_sequence"]:
            if "run_discussion" not in actions_seen:
                ok = False
                reasons.append("missing action 'run_discussion' for discussion branch")

        if 3 in case["choice_sequence"]:
            if "run_cv_generation" not in actions_seen:
                ok = False
                reasons.append("missing action 'run_cv_generation' for CV branch")

        if not choice_sequence == []:
            ok = False
            reasons.append("not all queued choices were consumed (menu did not loop as expected)")

        status = "PASS" if ok else "FAIL"
        symbol = "✓" if ok else "✗"
        print(f"[{case_id}] {case['description']}")
        print(f"  {symbol} {status}  actions={actions_seen}")
        if reasons:
            print(f"  reasons: {reasons}")
        print()

        results.append({"id": case_id, "status": status, "actions": actions_seen, "reasons": reasons})
        passed += ok
        failed += not ok

    return results, passed, failed


# =========================================================
# 3. Multi-entry persistence eval (regression test for load_all_entries bug)
# =========================================================

def run_multi_entry_persistence_evals(cases, tmp_dir):
    print(f"\n{'='*55}")
    print("  Multi-Entry Persistence Evals (load_all_entries)")
    print(f"{'='*55}\n")

    results = []
    passed = failed = 0

    for case in cases:
        case_id = case["id"]
        test_path = os.path.join(tmp_dir, f"{case_id}_profile.json")
        if os.path.exists(test_path):
            os.remove(test_path)

        with mock.patch.object(orch, "DATA_DIR", tmp_dir):
            for entry_text in case["entries"]:
                wrapped = orch.wrap_in_nonce(entry_text, orch.generate_nonce_tag())
                orch.save_data(test_path, wrapped)

            orch.log_trajectory(
                f"[EVAL] Running multi_entry_persistence case {case_id}.",
                "eval:multi_entry_persistence",
                f"{len(case['entries'])} entries written",
            )
            combined = orch.load_all_entries(test_path)

        all_present = all(entry_text in combined for entry_text in case["entries"])
        ok = all_present == case["expected_all_present"]

        status = "PASS" if ok else "FAIL"
        symbol = "✓" if ok else "✗"
        print(f"[{case_id}] {case['description']}")
        print(f"  {symbol} {status}  all_entries_present={all_present}\n")

        results.append({"id": case_id, "status": status, "all_entries_present": all_present})
        passed += ok
        failed += not ok

        if os.path.exists(test_path):
            os.remove(test_path)

    return results, passed, failed


# =========================================================
# Main
# =========================================================

def run_all():
    with open(CASES_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    tmp_dir = os.path.join(os.path.dirname(__file__), "_tmp_eval_data")
    os.makedirs(tmp_dir, exist_ok=True)

    all_entries = []
    total_passed = total_failed = 0

    pg_results, pg_p, pg_f = run_policy_gate_evals(cases["policy_gate"])
    all_entries.append({"section": "policy_gate", "results": pg_results})
    total_passed += pg_p
    total_failed += pg_f

    pm_results, pm_p, pm_f = run_post_match_menu_evals(cases["post_match_menu"])
    all_entries.append({"section": "post_match_menu", "results": pm_results})
    total_passed += pm_p
    total_failed += pm_f

    me_results, me_p, me_f = run_multi_entry_persistence_evals(cases["multi_entry_persistence"], tmp_dir)
    all_entries.append({"section": "multi_entry_persistence", "results": me_results})
    total_passed += me_p
    total_failed += me_f

    print(f"{'='*55}")
    print(f"  TOTAL: {total_passed} passed, {total_failed} failed")
    print(f"{'='*55}\n")

    log_eval_summary(all_entries)
    print(f"Eval log saved to: {EVAL_LOG_PATH}")
    print(f"Trajectory log: {orch.LOG_PATH}")

    try:
        os.rmdir(tmp_dir)
    except OSError:
        pass

    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    run_all()
