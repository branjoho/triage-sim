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
