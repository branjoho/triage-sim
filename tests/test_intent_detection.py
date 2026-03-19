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
