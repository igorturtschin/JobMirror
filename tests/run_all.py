#!/usr/bin/env python3
"""
JobMirror — единая точка запуска всех тестов/эвалов.

Запускает по порядку:
  1. pytest (test_discussion.py, test_cv_generation_trajectory.py, test_post_match_exit.py)
  2. run_skill_evals.py   (policy_gate + post_match_menu + persistence)
  3. run_match_eval.py    (требует OPENROUTER_API_KEY, реальные вызовы модели)
  4. run_pii_eval.py      (требует OPENROUTER_API_KEY, реальные вызовы модели)

Usage:
  python3 tests/run_all.py            # всё, включая live-эвалы (нужен ключ)
  python3 tests/run_all.py --no-live  # только pytest + skill_evals (без реальных API-вызовов)
"""
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")


def run(cmd, label):
    print(f"\n{'='*60}\n  {label}\n{'='*60}")
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode == 0


def main():
    no_live = "--no-live" in sys.argv
    results = {}

    results["pytest"] = run(
        [sys.executable, "-m", "pytest", "tests/", "-v",
         "-k", "test_discussion or test_cv_generation_trajectory or test_post_match_exit"],
        "pytest: discussion / cv-generation / post-match exit"
    )

    results["skill_evals"] = run(
        [sys.executable, "tests/run_skill_evals.py"],
        "run_skill_evals.py: policy_gate + post_match_menu + persistence"
    )

    if not no_live:
        results["match_eval"] = run(
            [sys.executable, "tests/run_match_eval.py"],
            "run_match_eval.py (live API)"
        )
        results["pii_eval"] = run(
            [sys.executable, "tests/run_pii_eval.py"],
            "run_pii_eval.py (live API)"
        )
    else:
        print("\n--no-live: пропускаем match_eval и pii_eval (нужен OPENROUTER_API_KEY)")

    print(f"\n{'='*60}\n  ИТОГ\n{'='*60}")
    for name, ok in results.items():
        print(f"  {'✓' if ok else '✗'} {name}")

    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
