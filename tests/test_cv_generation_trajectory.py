"""
Trajectory evals for the cv-generation skill (AGENTS.md p.4: Thought -> Tool
Call -> Observation, logged to logs/trajectory.log), rewritten against the
real ADK-based implementation in harness_orchestrator.py (post ADK
migration, Session 3).

run_cv_generation(profile_text, job_text, match_result) -> None:
  - has NO return value; drives HITL loops via get_user_choice()/input()
  - on final "Looks good, finish": writes data/cv.md and calls sys.exit(0)
  - the only model-call point is the module-level `_run_single_call()`
    helper (one-shot ADK LlmAgent call) — this is what we mock, not the
    old openai client.

Each test checks the recorded trajectory (logs/trajectory.log), not just
side effects, per AGENTS.md's audit requirement.

Run: OPENROUTER_API_KEY=dummy python3 -m pytest tests/test_cv_generation_trajectory.py -v
"""
import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

os.environ.setdefault("OPENROUTER_API_KEY", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness_orchestrator as h


def read_trajectory(log_path):
    with open(log_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def setup_clean_log(tmp_path, monkeypatch):
    log_path = tmp_path / "trajectory.log"
    monkeypatch.setattr(h, "LOG_PATH", str(log_path))
    monkeypatch.setattr(h, "LOG_DIR", str(tmp_path))
    return log_path


def setup_data_dir(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(h, "DATA_DIR", str(data_dir))
    return data_dir


# --- Case 1: Vibe Diff approved -> CV is generated and the full trajectory is logged ---

def test_cv_workflow_approved_generates_cv_and_logs_trajectory(tmp_path, monkeypatch):
    log_path = setup_clean_log(tmp_path, monkeypatch)
    data_dir = setup_data_dir(tmp_path, monkeypatch)

    fake_diff = "I will emphasize backend experience and downplay early-career retail work."
    fake_cv = "Summary: ...\nExperience: ...\nSkills: ..."

    with patch.object(h, "_run_single_call") as mock_call, \
         patch.object(h, "get_user_choice", side_effect=[1, 1]), \
         patch.object(h.sys, "exit", side_effect=SystemExit(0)) as mock_exit:  # 1=Approve diff, 1=Looks good finish
        mock_call.side_effect = [fake_diff, fake_cv]
        with pytest.raises(SystemExit):
            h.run_cv_generation("PROFILE TEXT", "JOB TEXT", {"match_level": "Strong"})

    assert mock_call.call_count == 2  # one for vibe diff, one for generation

    entries = read_trajectory(log_path)
    tool_calls = [e["tool_call"] for e in entries]

    # Trajectory must show: vibe diff produced -> approved -> CV generated -> saved -> finished
    assert "cv-generation:vibe_diff" in tool_calls
    assert any(e["tool_call"] == "cv-generation:vibe_diff" and e["observation"] == "approved"
               for e in entries)
    assert "cv-generation:generate" in tool_calls
    assert any(e["tool_call"] == "cv-generation:generate" and e["observation"] == "Done"
               for e in entries)
    assert any(e["tool_call"] == "cv-generation:save" and e["observation"] == "stored"
               for e in entries)
    assert any(e["tool_call"] == "cv-generation:finish" for e in entries)

    # CV actually written to disk
    cv_path = data_dir / "cv.md"
    assert cv_path.exists()
    assert cv_path.read_text(encoding="utf-8") == fake_cv


# --- Case 2: Vibe Diff rejected -> loop retries diff, CV generation is never called ---

def test_cv_workflow_rejected_diff_retries_without_generating_cv(tmp_path, monkeypatch):
    log_path = setup_clean_log(tmp_path, monkeypatch)
    setup_data_dir(tmp_path, monkeypatch)

    fake_diff_1 = "Strategy A."
    fake_diff_2 = "Strategy B."
    fake_cv = "Summary: ...\nExperience: ...\nSkills: ..."

    with patch.object(h, "_run_single_call") as mock_call, \
         patch.object(h, "get_user_choice", side_effect=[2, 1, 1]), \
         patch("builtins.input", side_effect=["I want more emphasis on leadership", "DONE"]), \
         patch.object(h.sys, "exit", side_effect=SystemExit(0)):
        # reject(2) -> revision text -> approve(1) diff2 -> finish(1)
        mock_call.side_effect = [fake_diff_1, fake_diff_2, fake_cv]
        with pytest.raises(SystemExit):
            h.run_cv_generation("PROFILE TEXT", "JOB TEXT", {"match_level": "Partial"})

    entries = read_trajectory(log_path)
    rejected = [e for e in entries if e["tool_call"] == "cv-generation:vibe_diff"
                and "revision requested" in e["thought"].lower()]
    approved = [e for e in entries if e["tool_call"] == "cv-generation:vibe_diff"
                and e["observation"] == "approved"]

    assert len(rejected) == 1
    assert len(approved) == 1
    # rejection must be logged BEFORE approval in the trajectory
    assert entries.index(rejected[0]) < entries.index(approved[0])

    # generation only happens once, only after approval
    gen_calls = [e for e in entries if e["tool_call"] == "cv-generation:generate" and e["observation"] == "Done"]
    assert len(gen_calls) == 1
    assert entries.index(gen_calls[0]) > entries.index(approved[0])

    # _run_single_call called 3 times: diff1, diff2, generation
    assert mock_call.call_count == 3


# --- Case 3: Revise after CV shown -> second full diff->generate cycle runs ---

def test_cv_workflow_revise_after_cv_runs_second_cycle(tmp_path, monkeypatch):
    log_path = setup_clean_log(tmp_path, monkeypatch)
    data_dir = setup_data_dir(tmp_path, monkeypatch)

    diff_1 = "Strategy A."
    cv_1 = "CV draft 1"
    diff_2 = "Strategy B."
    cv_2 = "CV draft 2"

    with patch.object(h, "_run_single_call") as mock_call, \
         patch.object(h, "get_user_choice", side_effect=[1, 2, 1, 1]), \
         patch.object(h.sys, "exit", side_effect=SystemExit(0)):
        # approve diff1 -> generate cv1 -> revise(2) -> approve diff2 -> generate cv2 -> finish(1)
        mock_call.side_effect = [diff_1, cv_1, diff_2, cv_2]
        with pytest.raises(SystemExit):
            h.run_cv_generation("PROFILE TEXT", "JOB TEXT", {"match_level": "Strong"})

    assert mock_call.call_count == 4

    entries = read_trajectory(log_path)
    gen_entries = [e for e in entries if e["tool_call"] == "cv-generation:generate" and e["observation"] == "Done"]
    diff_approved = [e for e in entries if e["tool_call"] == "cv-generation:vibe_diff" and e["observation"] == "approved"]

    # Two full cycles: 2 vibe diffs approved, 2 CVs generated
    assert len(diff_approved) == 2
    assert len(gen_entries) == 2

    # Final CV on disk is the second draft (revision overwrote the first)
    cv_path = data_dir / "cv.md"
    assert cv_path.read_text(encoding="utf-8") == cv_2


def test_cv_generation_never_fabricates_prompt_missing_profile_data():
    """Sanity check: the prompts sent to _run_single_call must contain the
    exact profile/job text passed in — zero-fabrication depends on this
    context actually reaching the model call."""
    with patch.object(h, "_run_single_call") as mock_call, \
         patch.object(h, "get_user_choice", side_effect=[1, 1]), \
         patch.object(h.sys, "exit", side_effect=SystemExit(0)):
        mock_call.side_effect = ["diff text", "cv text"]
        with pytest.raises(SystemExit):
            h.run_cv_generation("UNIQUE PROFILE MARKER", "UNIQUE JOB MARKER", {"match_level": "Strong"})

    vibe_prompt = mock_call.call_args_list[0].args[0]
    cv_prompt = mock_call.call_args_list[1].args[0]
    assert "UNIQUE PROFILE MARKER" in vibe_prompt
    assert "UNIQUE JOB MARKER" in vibe_prompt
    assert "UNIQUE PROFILE MARKER" in cv_prompt
    assert "UNIQUE JOB MARKER" in cv_prompt
