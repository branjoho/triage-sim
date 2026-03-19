# Richer Chat Responses Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace robotic scripted chat responses with Claude-generated natural-language responses (caregiver/patient voice for history, objective clinical voice for exam findings), and extend intent detection to 24 categories to reduce fallback rate.

**Architecture:** A one-time offline script (`generate_responses.py`) calls the Claude API once per case (20 calls), builds a prompt from clinical facts (blinded to ESI), and writes generated responses back to `cases.json`. `app.py` gains 10 new intent keyword categories. No runtime API dependency is introduced.

**Tech Stack:** Python 3, `anthropic` SDK (`pip install anthropic`), `pytest` for tests, existing Flask/SQLite app unchanged at runtime.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `app.py` | Modify lines ~174–209 | Add 10 new intent keyword lists; remove vaccine keywords from `pmh` |
| `generate_responses.py` | Create | Offline script: reads `cases.json`, calls Claude API, writes back new `chat_responses` |
| `tests/test_intent_detection.py` | Create | Tests for new and modified keyword mappings |
| `tests/test_generate_responses.py` | Create | Tests for prompt building, persona logic, validation |
| `cases.json` | Modified by script | `chat_responses` rewritten with generated content |
| `requirements.txt` | Modify | Add `anthropic>=0.25.0` and `pytest` |

---

## Task 1: Add test infrastructure

**Files:**
- Create: `tests/__init__.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Add dependencies to requirements.txt**

```
flask>=3.0.0
anthropic>=0.25.0
pytest>=8.0.0
```

- [ ] **Step 2: Create tests package**

```bash
mkdir tests && touch tests/__init__.py
```

- [ ] **Step 3: Verify pytest runs (empty suite)**

```bash
pytest tests/ -v
```

Expected: `no tests ran` — confirms pytest is installed and the package is found.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt tests/__init__.py
git commit -m "Add anthropic and pytest dependencies"
```

---

## Task 2: Extend intent keyword detection in app.py

**Files:**
- Modify: `app.py:174–209`
- Create: `tests/test_intent_detection.py`

### Background

`INTENT_KEYWORDS` is a dict at `app.py:174`. `detect_intent()` at line 211 scores each keyword list against the lowercased message and returns the highest-scoring intent (or `"unknown"` if score is 0).

The `pmh` entry currently includes `"vaccin"`, `"immuniz"`, `"shot"` — these must be removed to allow the new `immunization` category to fire.

- [ ] **Step 1: Write failing tests for new intents**

Create `tests/test_intent_detection.py`:

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import detect_intent

def test_hydration():
    assert detect_intent("Is she drinking okay?") == "hydration"

def test_fever_history():
    assert detect_intent("How long has she had a fever?") == "fever_history"

def test_behavior():
    assert detect_intent("How is he acting compared to normal?") == "behavior"

def test_feeding():
    assert detect_intent("Is she eating anything?") == "feeding"

def test_urinary():
    assert detect_intent("Any changes in urination?") == "urinary"
    # "urination" must be in keyword list, not just "urinating"

def test_exposure():
    assert detect_intent("Any sick contacts at daycare?") == "exposure"

def test_immunization():
    assert detect_intent("Is she up to date on vaccines?") == "immunization"

def test_family_history():
    assert detect_intent("Any relevant family history?") == "family_history"

def test_caregiver_concern():
    assert detect_intent("What are you most worried about?") == "caregiver_concern"

def test_review_of_systems():
    assert detect_intent("Any other symptoms?") == "review_of_systems"

def test_immunization_not_pmh():
    # Different phrasing — ensures immunization fires even without "up to date"
    assert detect_intent("Is he immunized?") == "immunization"

def test_pmh_still_works():
    assert detect_intent("Any past medical history?") == "pmh"

def test_unknown_still_works():
    assert detect_intent("xyzzy frobble wumble") == "unknown"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_intent_detection.py -v
```

Expected: all new intent tests FAIL (keywords not in dict yet).

- [ ] **Step 3: Update INTENT_KEYWORDS in app.py**

In `app.py`, make these two changes:

**a) Remove vaccine keywords from `pmh` (line ~200):**

```python
"pmh":          ["past","past medical","medical history","pmh","background","prior","previous",
                 "history of","chronic","diagnos","condition","problem","surgery","hospitali",
                 "birth","premature","baseline"],
```
(Remove `"vaccin"`, `"immuniz"`, `"shot"` from this list.)

**b) Add 10 new entries after the existing `interventions` entry (after line ~208):**

```python
    "hydration":        ["drinking","fluids","fluid intake","tears","thirsty","intake",
                         "dry mouth","diapers","wet diaper"],
    "fever_history":    ["how long fever","fever","tylenol","motrin","ibuprofen","antipyretic",
                         "temperature history","how long has","how long have"],
    "behavior":         ["acting","behavior","behaviour","irritable","fussy","lethargic",
                         "playful","herself","himself","themselves","baseline behavior",
                         "normal self"],
    "feeding":          ["eating","feeding","nursing","appetite","bottle","solids",
                         "breastfeed","breast feed","oral intake","refusing to eat"],
    "urinary":          ["urine","urinating","urination","pee","wet diapers","diaper count",
                         "urinary output","last void","void","last pee"],
    "exposure":         ["sick contact","daycare","day care","school","travel","exposed",
                         "contagious","been around","exposure"],
    "immunization":     ["up to date","immunized","last shot","vaccination record",
                         "last vaccine","vaccine schedule"],
    "family_history":   ["family history","family","hereditary","runs in the family","familial",
                         "genetic","family member"],
    # Note: "family history" scores 2 points (matches both "family" and "family history"),
    # ensuring it beats hpi's single "history" match in tie-breaking.
    "caregiver_concern":["worried about","most concerned","scared about","what do you think",
                         "most worried","what worries","what scares"],
    "review_of_systems":["anything else","other symptoms","head to toe","overall",
                         "everything","any other","review of systems","ros"],
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_intent_detection.py -v
```

Expected: all 13 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_intent_detection.py
git commit -m "Extend intent detection to 24 categories"
```

---

## Task 3: Write generate_responses.py

**Files:**
- Create: `generate_responses.py`
- Create: `tests/test_generate_responses.py`

### Background

The script:
1. Backs up `cases.json`
2. For each case, builds a prompt (clinical facts, blinded to ESI), determines persona type, calls Claude API
3. Validates the response has all 25 expected keys
4. Writes back to `cases.json`
5. Prints a summary

**Expected keys (25):** the 24 intent categories + `"unknown"`.

**Persona logic:**
- `age_years >= 12` → patient-as-speaker
- `vitals["gcs"] <= 8` → non-verbal/critical caregiver
- Otherwise → standard caregiver

**Two response voices in the prompt:**
- Exam-finding intents (`vitals`, `appearance`, `respiratory`, `neuro`, `skin`, `cardiac`, `abdominal`) → objective clinical findings, as the nurse would observe
- All other intents → caregiver/patient speaking naturally to the nurse

- [ ] **Step 1: Write failing unit tests**

Create `tests/test_generate_responses.py`:

```python
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from generate_responses import build_prompt, get_persona_type, validate_response, EXPECTED_KEYS

def make_case(age=5, gcs=15):
    return {
        "id": 1,
        "patient": {"age_years": age, "age_display": f"{age}-year-old", "sex": "Female", "weight_kg": 20},
        "chief_complaint": "Fever",
        "vitals": {"hr": 110, "rr": 22, "spo2": 98, "temp_c": 39.1, "bp": "95/60",
                   "cap_refill_sec": 2, "gcs": gcs},
        "hpi": "Fever for 2 days.",
        "pmh": "No past medical history.",
        "exam": "Alert child in mild distress.",
        "esi": 3,
        "ai_esi": 3,
        "correct_esi_rationale": "ESI 3 because...",
        "ai_rationale": "AI says ESI 3 because...",
    }

def test_persona_standard():
    assert get_persona_type(make_case(age=5, gcs=15)) == "standard"

def test_persona_patient_speaker():
    assert get_persona_type(make_case(age=14, gcs=15)) == "patient"

def test_persona_nonverbal():
    assert get_persona_type(make_case(age=5, gcs=8)) == "nonverbal"

def test_persona_nonverbal_critical_gcs():
    assert get_persona_type(make_case(age=15, gcs=6)) == "nonverbal"

def test_build_prompt_excludes_esi():
    prompt = build_prompt(make_case())
    assert "esi" not in prompt.lower()
    assert "correct_esi_rationale" not in prompt
    assert "ai_rationale" not in prompt

def test_build_prompt_includes_exam():
    prompt = build_prompt(make_case())
    assert "Alert child in mild distress" in prompt

def test_build_prompt_includes_vitals():
    prompt = build_prompt(make_case())
    assert "110" in prompt  # HR

def test_validate_response_passes_complete():
    complete = {k: "response" for k in EXPECTED_KEYS}
    assert validate_response(complete) is True

def test_validate_response_fails_missing_key():
    incomplete = {k: "response" for k in EXPECTED_KEYS if k != "unknown"}
    assert validate_response(incomplete) is False

def test_validate_response_fails_extra_keys_only():
    # Extra keys are fine as long as all expected keys present
    complete = {k: "response" for k in EXPECTED_KEYS}
    complete["extra"] = "bonus"
    assert validate_response(complete) is True
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_generate_responses.py -v
```

Expected: all tests FAIL (`generate_responses` module not found).

- [ ] **Step 3: Write generate_responses.py**

```python
#!/usr/bin/env python3
"""
Offline script: generates richer chat_responses for all cases in cases.json
using the Claude API. Run once; re-run if cases change.

Usage:
    ANTHROPIC_API_KEY=<key> python generate_responses.py

Requires: pip install anthropic
"""
import json
import os
import shutil
import time
from datetime import date
import anthropic

CASES_FILE = os.path.join(os.path.dirname(__file__), "cases.json")
MODEL = "claude-opus-4-5-20250514"
TEMPERATURE = 0.3

EXAM_INTENTS = {"vitals", "appearance", "respiratory", "neuro", "skin", "cardiac", "abdominal"}

EXPECTED_KEYS = {
    "vitals", "appearance", "respiratory", "neuro", "skin", "cardiac", "abdominal",
    "hpi", "onset", "pmh", "medications", "allergies", "pain", "interventions",
    "hydration", "fever_history", "behavior", "feeding", "urinary", "exposure",
    "immunization", "family_history", "caregiver_concern", "review_of_systems",
    "unknown",
}


def get_persona_type(case: dict) -> str:
    age = case["patient"]["age_years"]
    gcs = case["vitals"].get("gcs")
    if gcs is not None and gcs <= 8:
        return "nonverbal"
    if age >= 12:
        return "patient"
    return "standard"


def build_prompt(case: dict) -> str:
    p = case["patient"]
    v = case["vitals"]
    persona_type = get_persona_type(case)

    if persona_type == "patient":
        persona = (
            f"You are the patient — a {p['age_display']} {p['sex'].lower()}. "
            "Respond naturally as you would speaking directly to an ED nurse. "
            "You do not know the medical severity of your condition."
        )
    elif persona_type == "nonverbal":
        persona = (
            "You are the parent or caregiver. The patient may not have been able to speak. "
            "You may not know details of what happened after EMS arrived. "
            "Respond based only on what you witnessed. "
            "For clinical findings you could not observe, say 'I don't know, I wasn't there for that part.'"
        )
    else:
        persona = (
            f"You are the parent or caregiver of this {p['age_display']} {p['sex'].lower()} patient. "
            "You brought them to the ED. Respond naturally as you would speaking directly to an ED nurse. "
            "You do not know the medical severity of their condition."
        )

    vitals_str = (
        f"HR {v.get('hr')}, RR {v.get('rr')}, SpO2 {v.get('spo2')}%, "
        f"Temp {v.get('temp_c')}°C, BP {v.get('bp')}, "
        f"Cap refill {v.get('cap_refill_sec')}s"
    )

    categories = sorted(EXPECTED_KEYS - {"unknown"})

    return f"""You are helping generate realistic chat responses for a nursing simulation study.

PERSONA: {persona}

CASE INFORMATION (use this to ground your responses — do NOT reveal any severity assessment):
- Patient: {p['age_display']}, {p['sex']}, {p['weight_kg']} kg
- Chief complaint: {case['chief_complaint']}
- Vitals: {vitals_str}
- History: {case['hpi']}
- Past medical history: {case['pmh']}
- Exam findings (for nurse-observed responses only): {case['exam']}

TASK: Generate one response per category below. Follow these voice rules strictly:

EXAM-FINDING CATEGORIES ({', '.join(sorted(EXAM_INTENTS))}):
Write as objective clinical findings — what the nurse would observe or measure on assessment.
Example: "Child appears pale and lethargic, making poor eye contact."

ALL OTHER CATEGORIES:
Write in the persona voice above — natural spoken language, as if talking to a nurse.
Example: "She's been refusing the bottle since this morning, maybe had two wet diapers today."

FALLBACK ("unknown"): Write a case-appropriate "I'm not sure what you mean — can you ask that differently?" response in the persona voice.

Return ONLY a valid JSON object with exactly these keys (no markdown, no explanation):
{json.dumps(categories + ["unknown"], indent=2)}
"""


def validate_response(data: dict) -> bool:
    return EXPECTED_KEYS.issubset(data.keys())


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ERROR: ANTHROPIC_API_KEY environment variable not set.")

    with open(CASES_FILE) as f:
        cases = json.load(f)

    # Backup
    backup_path = f"{CASES_FILE}.bak.{date.today()}"
    shutil.copy(CASES_FILE, backup_path)
    print(f"Backup written to {backup_path}")

    client = anthropic.Anthropic(api_key=api_key)
    updated, skipped, errors = [], [], []

    for case in cases:
        case_id = case["id"]
        print(f"Case {case_id}: {case['title']} ...", end=" ", flush=True)

        try:
            prompt = build_prompt(case)
            message = client.messages.create(
                model=MODEL,
                max_tokens=2048,
                temperature=TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text.strip()

            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            data = json.loads(raw)

            if not validate_response(data):
                missing = EXPECTED_KEYS - data.keys()
                print(f"SKIP (missing keys: {missing})")
                skipped.append(case_id)
                continue

            case["chat_responses"] = data
            updated.append(case_id)
            print("OK")

        except json.JSONDecodeError as e:
            print(f"ERROR (JSON parse: {e})")
            errors.append(case_id)
        except Exception as e:
            print(f"ERROR ({e})")
            errors.append(case_id)

        time.sleep(0.5)

    with open(CASES_FILE, "w") as f:
        json.dump(cases, f, indent=2)

    print(f"\nDone. Updated: {len(updated)}, Skipped: {len(skipped)}, Errors: {len(errors)}")
    if skipped:
        print(f"  Skipped cases: {skipped}")
    if errors:
        print(f"  Error cases: {errors}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_generate_responses.py -v
```

Expected: all 10 tests PASS.

- [ ] **Step 5: Run full test suite**

```bash
pytest tests/ -v
```

Expected: all tests PASS (intent detection + generate_responses).

- [ ] **Step 6: Commit**

```bash
git add generate_responses.py tests/test_generate_responses.py
git commit -m "Add offline response generation script with tests"
```

---

## Task 4: Run generation and update cases.json

**Files:**
- Modify: `cases.json` (via script)

- [ ] **Step 1: Install anthropic**

```bash
pip install anthropic>=0.25.0
```

- [ ] **Step 2: Set API key and run script**

```bash
ANTHROPIC_API_KEY=<your-key> python generate_responses.py
```

Expected output (roughly):
```
Backup written to cases.json.bak.2026-03-19
Case 1: Apneic Infant in Waiting Room ... OK
Case 2: Anaphylaxis Post-Peanut Exposure ... OK
...
Done. Updated: 20, Skipped: 0, Errors: 0
```

If any cases are skipped or errored, re-run for those cases only (edit script temporarily to filter by ID).

- [ ] **Step 3: Spot-check cases.json**

Verify:
- Each case has 25 keys in `chat_responses` (24 intents + `"unknown"`)
- A caregiver-voice entry sounds natural (e.g., check `case[0]["chat_responses"]["hpi"]`)
- An exam-finding entry sounds clinical (e.g., check `case[0]["chat_responses"]["appearance"]`)
- `"unknown"` fallback is case-specific and in caregiver voice

```bash
python3 -c "
import json
cases = json.load(open('cases.json'))
for c in cases:
    keys = set(c['chat_responses'].keys())
    expected = 25
    print(f'Case {c[\"id\"]}: {len(keys)} keys {\"OK\" if len(keys) == expected else \"WARN\"}')
"
```

Expected: all 20 cases print `25 keys OK`.

- [ ] **Step 4: Commit**

```bash
git add cases.json
git commit -m "Regenerate chat responses with natural caregiver/clinical voice"
```

---

## Task 5: Manual smoke test

- [ ] **Step 1: Start the app**

```bash
PORT=5001 python app.py
```

- [ ] **Step 2: Register a test nurse and run through one case**

- Open `http://localhost:5001`
- Register a new nurse account
- Start the simulation
- In the chat, ask questions that exercise new intents:
  - "Is she drinking okay?" → should get a hydration response (not generic fallback)
  - "Any sick contacts?" → should get an exposure response
  - "How long has she had this fever?" → should get a fever_history response
  - "What are you most worried about?" → should get a caregiver_concern response
  - "xyzzy frobble" → should get the case-specific unknown fallback (not the hardcoded generic one)

- [ ] **Step 3: Commit and push**

```bash
git push
```

---

## Notes

- `cases.json.bak.<date>` is created automatically by the script. Add `cases.json.bak.*` to `.gitignore` if desired.
- The `ANTHROPIC_API_KEY` is never committed — pass it via environment variable only.
- To regenerate a single case, temporarily wrap the `for case in cases` loop with `if case["id"] != <N>: continue`.
- Model is pinned to `claude-opus-4-5-20250514`. Verify this model ID is valid before running all 20 cases (a quick single-case test run will confirm). If the model is deprecated, update `MODEL` and re-run all cases for consistency.
- The spec references an "EMS-only flag" for the nonverbal persona — no such field exists in `cases.json`. The GCS threshold (`<= 8`) covers all critical cases in the dataset. No schema change needed.
- `cases.json.bak.*` files are safe to add to `.gitignore`.
