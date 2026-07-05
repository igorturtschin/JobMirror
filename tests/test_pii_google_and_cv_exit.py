"""
Unit tests for PII classification helpers in harness_orchestrator.py.

These tests cover the [[REVIEWED:...]] marker mechanism — the design that
prevents the PII scanner from re-flagging a fragment the user has already
reviewed and decided to keep (category 5 = not PII).

No live API calls — OPENROUTER_API_KEY=dummy is sufficient.
Run: python3 -m pytest tests/test_pii_google_and_cv_exit.py -v
"""
import os
import sys

os.environ.setdefault("OPENROUTER_API_KEY", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness_orchestrator as h


def test_classify_not_pii_marks_reviewed_so_rescan_wont_find_it():
    """Category 5 (not PII) must replace the fragment with [[REVIEWED:fragment]]
    rather than leaving the literal word in place. This prevents scan_for_pii
    from re-flagging the same word on the next scan iteration and asking the
    user to classify it again."""
    text = "I worked at Google for 5 years."
    result = h.classify_pii_fragment(text, "Google", 5)
    assert result["status"] == "kept"
    assert "[[REVIEWED:Google]]" in result["sanitized_text"]
    assert "Google" not in result["sanitized_text"].replace("[[REVIEWED:Google]]", "")


def test_strip_reviewed_markers_restores_original():
    """Before saving to profile.json, [[REVIEWED:...]] markers must be stripped
    back to the original word. The markers are internal scaffolding only —
    they must never appear in the persisted profile data."""
    text = "I worked at [[REVIEWED:Google]] for 5 years."
    assert h._strip_reviewed_markers(text) == "I worked at Google for 5 years."