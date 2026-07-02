import json
import os
import sys
from unittest.mock import patch

os.environ.setdefault("OPENROUTER_API_KEY", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness_orchestrator as h


def test_classify_not_pii_marks_reviewed_so_rescan_wont_find_it():
    text = "I worked at Google for 5 years."
    result = h.classify_pii_fragment(text, "Google", 5)
    assert result["status"] == "kept"
    assert "[[REVIEWED:Google]]" in result["sanitized_text"]
    assert "Google" not in result["sanitized_text"].replace("[[REVIEWED:Google]]", "")


def test_strip_reviewed_markers_restores_original():
    text = "I worked at [[REVIEWED:Google]] for 5 years."
    assert h._strip_reviewed_markers(text) == "I worked at Google for 5 years."


def test_post_match_menu_exits_after_cv_finish(tmp_path, monkeypatch):
    monkeypatch.setattr(h, "LOG_PATH", str(tmp_path / "trajectory.log"))
    monkeypatch.setattr(h, "LOG_DIR", str(tmp_path))
    monkeypatch.setattr(h, "PROFILE_PATH", str(tmp_path / "profile.json"))
    monkeypatch.setattr(h, "JOB_PATH", str(tmp_path / "job.json"))
    monkeypatch.setattr(h, "DATA_DIR", str(tmp_path / "data"))

    for path, label in [(h.PROFILE_PATH, "PROFILE"), (h.JOB_PATH, "JOB")]:
        with open(path, "w") as f:
            json.dump([{"timestamp": "x", "content": label}], f)

    with patch.object(h, "_run_single_call") as mock_call, \
         patch.object(h.sys, "exit", side_effect=SystemExit(0)), \
         patch("builtins.input", side_effect=["3", "1", "1"]):
        mock_call.side_effect = ["diff", "cv text"]
        try:
            h.run_post_match_menu("TESTNONCE", {"match_level": "Strong"})
            exited = False
        except SystemExit:
            exited = True

    assert exited, "run_post_match_menu must exit via sys.exit, not loop back to menu"