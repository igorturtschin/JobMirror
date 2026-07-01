"""
Trajectory eval: post-match menu exits after the CV workflow completes
(choice 3 + finish), rewritten against the real ADK-based implementation
in harness_orchestrator.py (post ADK migration, Session 3).

This is an end-to-end integration test: it drives run_post_match_menu()
through real input()/get_user_choice() (not mocked, only stdin is faked)
and the real run_cv_generation() HITL loop, mocking only the single model
call point (_run_single_call) and sys.exit (to catch the real exit signal
instead of killing the test process).
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


def test_post_match_menu_exits_after_cv_finish(tmp_path, monkeypatch):
    monkeypatch.setattr(h, "LOG_PATH", str(tmp_path / "trajectory.log"))
    monkeypatch.setattr(h, "LOG_DIR", str(tmp_path))
    monkeypatch.setattr(h, "PROFILE_PATH", str(tmp_path / "profile.json"))
    monkeypatch.setattr(h, "JOB_PATH", str(tmp_path / "job.json"))
    monkeypatch.setattr(h, "DATA_DIR", str(tmp_path / "data"))

    # Write minimal profile and job so load_all_entries returns something
    for path, label in [(h.PROFILE_PATH, "PROFILE"), (h.JOB_PATH, "JOB")]:
        with open(path, "w") as f:
            json.dump([{"timestamp": "x", "content": label}], f)

    fake_diff = "I will emphasize X."
    fake_cv = "# CV\nSummary: great candidate."

    with patch.object(h, "_run_single_call") as mock_call, \
         patch.object(h.sys, "exit", side_effect=SystemExit(0)), \
         patch("builtins.input", side_effect=[
             "3",   # post-match menu: Proceed to CV
             "1",   # approve vibe diff
             "1",   # looks good, finish
         ]):
        mock_call.side_effect = [fake_diff, fake_cv]
        # run_post_match_menu must exit via SystemExit (not loop forever)
        with pytest.raises(SystemExit):
            h.run_post_match_menu("TESTNONCE", {"match_level": "Strong"})

    entries = read_trajectory(str(tmp_path / "trajectory.log"))
    tool_calls = [e["tool_call"] for e in entries]

    # CV workflow ran: vibe diff produced+approved, CV generated
    assert "cv-generation:vibe_diff" in tool_calls
    assert "cv-generation:generate" in tool_calls
    assert any(e["tool_call"] == "cv-generation:vibe_diff" and e["observation"] == "approved"
               for e in entries)
    assert any(e["tool_call"] == "cv-generation:generate" and e["observation"] == "Done"
               for e in entries)

    # Session ended: save + finish logged
    assert any(e["tool_call"] == "cv-generation:save" and e["observation"] == "stored"
               for e in entries)
    assert any(e["tool_call"] == "cv-generation:finish" for e in entries)

    # CV file created (DATA_DIR is module-level constant, use h.DATA_DIR)
    cv_path = os.path.join(h.DATA_DIR, "cv.md")
    assert os.path.exists(cv_path)
    with open(cv_path, encoding="utf-8") as f:
        assert f.read() == fake_cv
