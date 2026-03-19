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
