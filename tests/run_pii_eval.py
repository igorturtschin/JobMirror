import json
import os
import sys
import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
EVAL_PATH = os.path.join(os.path.dirname(__file__), "pii_eval.json")
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "pii_eval.log")
MODEL = "google/gemini-2.5-flash-lite"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


def get_now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"


def call_pii_scan(text: str) -> list:
    prompt = (
        "TASK: Identify ALL personal data in the text: Names, Emails, Phones, Addresses. "
        "Return ONLY a JSON object with the key 'found'. Example: {\"found\": [\"Ivan\", \"test@mail.com\"]}."
        f"\nText: {text}"
    )
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    raw = completion.choices[0].message.content
    return json.loads(raw).get("found", [])


def normalize(items: list) -> set:
    """Lowercase + strip for fuzzy comparison."""
    return {i.lower().strip() for i in items}


def words(items: list) -> set:
    """Flatten all items into individual lowercase words for subset matching."""
    result = set()
    for item in items:
        for word in item.lower().split():
            result.add(word.strip(",."))
    return result


def run_evals():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    results = []
    passed = 0
    failed = 0

    print(f"\n{'='*55}")
    print(f"  JobMirror PII Eval Suite — {MODEL}")
    print(f"{'='*55}\n")

    for case in cases:
        case_id = case["id"]
        description = case["description"]
        text = case["input"]
        expected = case["expected_pii"]
        expect_found = case["expect_pii_found"]

        print(f"[{case_id}] {description}")

        try:
            found = call_pii_scan(text)
        except Exception as e:
            print(f"  ERROR: API call failed — {e}\n")
            results.append({
                "id": case_id, "status": "ERROR", "error": str(e),
                "timestamp": get_now_iso()
            })
            failed += 1
            continue

        found_words = words(found)
        expected_words = words(expected)

        if expect_found:
            # All words from expected items must appear somewhere in found items
            missing = expected_words - found_words
            ok = len(missing) == 0
            extra = set()
        else:
            # No PII should be found
            ok = len(found) == 0
            missing = set()
            extra = normalize(found)

        status = "PASS" if ok else "FAIL"
        symbol = "✓" if ok else "✗"

        print(f"  {symbol} {status}")
        print(f"  Expected : {expected}")
        print(f"  Got      : {found}")
        if not ok:
            if missing:
                print(f"  Missing  : {sorted(missing)}")
            if extra and not expect_found:
                print(f"  False pos: {sorted(extra)}")
        print()

        log_entry = {
            "id": case_id,
            "status": status,
            "expected": expected,
            "found": found,
            "missing": sorted(missing) if missing else [],
            "false_positives": sorted(extra) if (extra and not expect_found) else [],
            "timestamp": get_now_iso(),
        }
        results.append(log_entry)

        if ok:
            passed += 1
        else:
            failed += 1

    # --- Summary ---
    total = len(cases)
    print(f"{'='*55}")
    print(f"  Results: {passed}/{total} passed, {failed}/{total} failed")
    print(f"{'='*55}\n")

    # --- Log ---
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "run_timestamp": get_now_iso(),
            "model": MODEL,
            "summary": {"total": total, "passed": passed, "failed": failed},
            "cases": results,
        }, ensure_ascii=False) + "\n")

    print(f"Log saved to: {LOG_PATH}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    run_evals()