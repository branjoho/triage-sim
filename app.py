"""
Pediatric ESI Triage Simulation — Flask Backend (Chat Interface)
=================================================================
Research design:
  Arm A (Baseline-first): Nurse sees case → submits ESI → sees AI recommendation → may revise → sees feedback
  Arm B (AI-first):       Nurse sees case + AI recommendation upfront → submits ESI → sees feedback

Chat-based information gathering:
  Instead of progressive disclosure cards, nurses ask questions via chat.
  All responses are pre-scripted and stored in case.chat_responses.
  Intent detection identifies which category the question addresses.
  Same question always gets the same answer (no runtime generation).

Data captured per response:
  nurse_id, case_id, arm, initial_esi, initial_confidence, final_esi, final_confidence,
  correct_esi, ai_esi, response_time_ms, revision_time_ms, changed_after_ai, direction_of_change,
  n_chat_messages (count of messages in chat), unique_intents_asked (JSON array), first_intent,
  session_id, timestamp

Chat messages logged separately:
  sender (nurse|system|ai), content, intent, section, message_index, elapsed_ms, timestamp
"""

import os, json, sqlite3, secrets, hashlib, csv, io, random
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, request, jsonify,
                   session, redirect, url_for, send_file, g)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE  = os.path.join(BASE_DIR, "triage_sim.db")
CASES_FILE = os.path.join(BASE_DIR, "cases.json")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "triage_admin_2024")

# ─── DB helpers ────────────────────────────────────────────────────────────────

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
    return db

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE IF NOT EXISTS nurses (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT    UNIQUE NOT NULL,
            password_hash   TEXT    NOT NULL,
            arm_sequence    TEXT    NOT NULL,   -- JSON array: "A"|"B" per case index
            case_sequence   TEXT,               -- JSON array of case IDs in randomized presentation order
            years_experience INTEGER,
            role            TEXT,               -- RN, NP, charge, student, etc.
            work_setting    TEXT,               -- ED, PICU, gen peds, etc.
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sim_sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nurse_id        INTEGER NOT NULL,
            started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at    TIMESTAMP,
            cases_completed INTEGER DEFAULT 0,
            FOREIGN KEY (nurse_id) REFERENCES nurses(id)
        );

        CREATE TABLE IF NOT EXISTS responses (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            nurse_id                INTEGER NOT NULL,
            session_id              INTEGER NOT NULL,
            case_id                 INTEGER NOT NULL,
            case_order              INTEGER NOT NULL,   -- position in this session (1-based)
            arm                     TEXT    NOT NULL,   -- "A" or "B"
            initial_esi             INTEGER,
            initial_confidence      INTEGER,            -- 1 (very uncertain) to 5 (very confident)
            final_esi               INTEGER,            -- null if no revision (arm A) or = initial_esi (arm B)
            final_confidence        INTEGER,
            correct_esi             INTEGER NOT NULL,
            ai_esi                  INTEGER NOT NULL,
            ai_correct              INTEGER NOT NULL,   -- 0/1
            initial_correct         INTEGER,            -- 0/1 computed at submission
            final_correct           INTEGER,            -- 0/1
            changed_after_ai        INTEGER,            -- 0/1, arm A only
            direction_of_change     TEXT,               -- "higher","lower","none", arm A only
            response_time_ms        INTEGER,            -- case load → initial submit (ms)
            revision_time_ms        INTEGER,            -- ai reveal → revision submit (arm A, ms)
            info_seeking_log        TEXT,               -- JSON [{section, revealed_at_ms}, ...]
            sections_revealed_count INTEGER DEFAULT 0,  -- 0-3 (hpi/exam/pmh)
            revealed_hpi            INTEGER DEFAULT 0,  -- 0/1
            revealed_exam           INTEGER DEFAULT 0,  -- 0/1
            revealed_pmh            INTEGER DEFAULT 0,  -- 0/1
            hpi_reveal_ms           INTEGER,            -- ms from case load to HPI click
            exam_reveal_ms          INTEGER,            -- ms from case load to Exam click
            pmh_reveal_ms           INTEGER,            -- ms from case load to PMH click
            free_text_reasoning     TEXT,               -- optional nurse notes
            n_chat_messages         INTEGER DEFAULT 0,  -- count of chat messages in this case
            unique_intents_asked    TEXT,               -- JSON array of unique intents asked
            first_intent            TEXT,               -- very first intent asked
            working_hypothesis      TEXT,               -- NCJMM: nurse's primary working concern
            cue_salience            TEXT,               -- NCJMM: JSON array of intents nurse flagged as key
            timestamp               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nurse_id)  REFERENCES nurses(id),
            FOREIGN KEY (session_id) REFERENCES sim_sessions(id)
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nurse_id        INTEGER NOT NULL,
            session_id      INTEGER NOT NULL,
            case_id         INTEGER NOT NULL,
            case_order      INTEGER NOT NULL,
            arm             TEXT    NOT NULL,
            sender          TEXT    NOT NULL,  -- "nurse" | "system" | "ai"
            content         TEXT    NOT NULL,
            intent          TEXT,              -- detected intent for nurse messages
            section         TEXT,              -- which section this maps to
            message_index   INTEGER NOT NULL,  -- 1-based within this case
            elapsed_ms      INTEGER,           -- ms from case load
            timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nurse_id)  REFERENCES nurses(id),
            FOREIGN KEY (session_id) REFERENCES sim_sessions(id)
        );
    """)
    db.commit()

    # Schema migration: safely add new columns to existing databases.
    # SQLite has no IF NOT EXISTS for ALTER TABLE, so we catch the error.
    new_columns = [
        ("nurses",    "case_sequence",          "TEXT"),
        ("responses", "n_chat_messages",        "INTEGER DEFAULT 0"),
        ("responses", "unique_intents_asked",   "TEXT"),
        ("responses", "first_intent",           "TEXT"),
        ("responses", "working_hypothesis",     "TEXT"),
        ("responses", "cue_salience",           "TEXT"),
        ("responses", "ai_influence",           "TEXT"),
    ]
    for table, col, typedef in new_columns:
        try:
            db.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typedef}")
        except Exception:
            pass  # column already exists
    db.commit()
    db.close()

# ─── Case loading ──────────────────────────────────────────────────────────────

CASES = []

def load_cases():
    global CASES
    with open(CASES_FILE) as f:
        CASES = json.load(f)

def get_case_by_id(case_id):
    for c in CASES:
        if c["id"] == case_id:
            return c
    return None

# ─── Intent detection ──────────────────────────────────────────────────────────

INTENT_KEYWORDS = {
    "vitals":       ["vital","heart rate"," hr ","hr,","hrr","blood pressure","bp","temp","spo2",
                     "oxygen","sat","o2","respiratory rate","rr","gcs","glasgow","cap refill",
                     "capillary","pulse","pressure","sign"],
    "appearance":   ["look","appear","seem","general","overall","how does","what does","presenting",
                     "awake","alert","conscious","responsive","well","sick","ill","distress"],
    "respiratory":  ["breath","breathing","lung","chest","airway","stridor","wheeze","wheez",
                     "cough","retractions","retract","auscult","air entry","crackle","grunt",
                     "flare","nasal","respiratory"],
    "neuro":        ["neuro","mental status","gcs","glasgow","consciousness","alert","orient",
                     "pupils","pupil","fontanelle","fontan","seizure","posture","tone","reflex",
                     "mental","cognitive","responsive","unresponsive","awake"],
    "skin":         ["skin","rash","color","colour","cyanosis","cyanotic","petechiae","purpura",
                     "urticaria","hive","pallor","pale","jaundice","wound","bruise","ecchymos",
                     "lacerat","abrasion","swelling","edema","mottl"],
    "cardiac":      ["heart","cardiac","rhythm","murmur","palpitation","pulse","perfusion",
                     "capillary refill","cardiovascular","rate","tachy","brady"],
    "abdominal":    ["abdomen","abdominal","belly","stomach","bowel","nausea","vomit","gi ",
                     "guarding","tender","rigidity","distension","appendic","pain in","rlq","llq"],
    "hpi":          ["history","hpi","what happened","when did","how long","onset","duration",
                     "symptom","complaint","sick","ill","describe","tell me","more about",
                     "reason","presenting","presenting complaint","illness",
                     "what brings you","why are you here","what has been going on",
                     "what's been going on","whats been going on","what is going on",
                     "what's going on","going on","brings you in","what symptoms"],
    "onset":        ["when","how long","start","began","duration","onset","since","ago",
                     "first","timing","how did it start","how long ago"],
    "pmh":          ["past","past medical","medical history","pmh","background","prior","previous",
                     "history of","chronic","diagnos","condition","problem","surgery","hospitali",
                     "birth","premature","baseline"],
    "medications":  ["medic","med ","meds","drug","prescription","rx","pill","tablet",
                     "dose","dosing","taking","on any","currently on","home med"],
    "allergies":    ["allerg","allergic","reaction","sensitivity","intolerance","drug allergy"],
    "pain":         ["pain","hurt","ache","tender","sore","discomfort","score","scale",
                     "how much","10","rate","pain level","pain score","faces"],
    "interventions":["done","given","treated","treatment","intervention","manag","prior",
                     "before arrival","ems","paramedic","prehospital","pre-hospital","already",
                     "administer","receive","receiv"],
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
    "caregiver_concern":["worried about","most concerned","scared about","what do you think",
                         "most worried","what worries","what scares"],
    "review_of_systems":["anything else","other symptoms","head to toe","overall",
                         "everything","any other","review of systems","ros"],
}

def detect_intent(message: str) -> str:
    """Detect which category (intent) a message is asking about."""
    msg = message.lower()
    scores = {intent: 0 for intent in INTENT_KEYWORDS}
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in msg:
                scores[intent] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"

# ─── Auth helpers ──────────────────────────────────────────────────────────────

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "nurse_id" not in session:
            return jsonify({"error": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            return jsonify({"error": "Admin only"}), 403
        return f(*args, **kwargs)
    return decorated

# ─── Arm sequence generation ───────────────────────────────────────────────────

# Stratified counterbalancing groups — balanced by ESI level and AI error count.
# Group 0: ESI1×2, ESI2×3, ESI3×2, ESI4×2, ESI5×1 | 3 AI errors (cases 4,9,16)
# Group 1: ESI1×1, ESI2×3, ESI3×3, ESI4×2, ESI5×1 | 4 AI errors (cases 7,13,14,18)
_CB_GROUP_0 = [1, 2,  4, 5, 10,  9, 11,  16, 17,  19]
_CB_GROUP_1 = [3,     6, 7,  8, 12, 13, 14,  15, 18,  20]

def generate_counterbalanced_sequences(nurse_number):
    """
    Stratified counterbalancing:
    - Cases pre-split into two ESI-matched groups (_CB_GROUP_0, _CB_GROUP_1).
    - Even nurses: Group 0 → Arm A, Group 1 → Arm B.
      Odd nurses:  Group 0 → Arm B, Group 1 → Arm A.
    - Within-group rotation (every 2 nurses) counterbalances case positions.
    - Interleave pattern shifts each nurse so A/B don't always occupy the same serial positions.
    """
    if nurse_number % 2 == 0:
        a_cases, b_cases = _CB_GROUP_0[:], _CB_GROUP_1[:]
    else:
        a_cases, b_cases = _CB_GROUP_1[:], _CB_GROUP_0[:]

    rotation = (nurse_number // 2) % 10
    a_cases = a_cases[rotation:] + a_cases[:rotation]
    b_cases = b_cases[rotation:] + b_cases[:rotation]

    case_seq, arm_seq = [], []
    for i in range(10):
        if nurse_number % 2 == 0:
            case_seq += [a_cases[i], b_cases[i]]
            arm_seq  += ["A", "B"]
        else:
            case_seq += [b_cases[i], a_cases[i]]
            arm_seq  += ["B", "A"]
    return case_seq, arm_seq

# ─── Routes: Auth ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    years    = data.get("years_experience")
    role     = (data.get("role") or "").strip()
    setting  = (data.get("work_setting") or "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM nurses WHERE username=?", (username,)).fetchone()
    if existing:
        return jsonify({"error": "Username already taken"}), 409

    nurse_number = db.execute("SELECT COUNT(*) as n FROM nurses").fetchone()["n"]
    case_seq, arm_seq = generate_counterbalanced_sequences(nurse_number)
    db.execute(
        "INSERT INTO nurses (username, password_hash, arm_sequence, case_sequence, years_experience, role, work_setting) "
        "VALUES (?,?,?,?,?,?,?)",
        (username, hash_pw(password), json.dumps(arm_seq), json.dumps(case_seq), years, role, setting)
    )
    db.commit()
    nurse = db.execute("SELECT * FROM nurses WHERE username=?", (username,)).fetchone()
    session["nurse_id"]  = nurse["id"]
    session["username"]  = nurse["username"]
    session["is_admin"]  = False
    return jsonify({"ok": True, "nurse_id": nurse["id"], "username": nurse["username"]})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Admin shortcut
    if username == "admin" and password == ADMIN_PASSWORD:
        session["is_admin"] = True
        session["username"] = "admin"
        return jsonify({"ok": True, "is_admin": True})

    db = get_db()
    nurse = db.execute(
        "SELECT * FROM nurses WHERE username=? AND password_hash=?",
        (username, hash_pw(password))
    ).fetchone()
    if not nurse:
        return jsonify({"error": "Invalid credentials"}), 401

    session["nurse_id"] = nurse["id"]
    session["username"] = nurse["username"]
    session["is_admin"] = False
    return jsonify({"ok": True, "nurse_id": nurse["id"], "username": nurse["username"], "is_admin": False})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/me")
def me():
    if "nurse_id" not in session and not session.get("is_admin"):
        return jsonify({"authenticated": False})
    return jsonify({
        "authenticated": True,
        "nurse_id": session.get("nurse_id"),
        "username": session.get("username"),
        "is_admin": session.get("is_admin", False)
    })

# ─── Routes: Session management ────────────────────────────────────────────────

@app.route("/api/session/start", methods=["POST"])
@login_required
def start_sim_session():
    db = get_db()
    # Check for an incomplete session
    open_session = db.execute(
        "SELECT * FROM sim_sessions WHERE nurse_id=? AND completed_at IS NULL ORDER BY started_at DESC LIMIT 1",
        (session["nurse_id"],)
    ).fetchone()
    if open_session:
        completed_cases = db.execute(
            "SELECT COUNT(*) as n FROM responses WHERE session_id=?",
            (open_session["id"],)
        ).fetchone()["n"]
        return jsonify({
            "session_id": open_session["id"],
            "resumed": True,
            "cases_completed": completed_cases,
            "total_cases": len(CASES)
        })

    db.execute(
        "INSERT INTO sim_sessions (nurse_id) VALUES (?)", (session["nurse_id"],)
    )
    db.commit()
    new_session = db.execute(
        "SELECT * FROM sim_sessions WHERE nurse_id=? ORDER BY started_at DESC LIMIT 1",
        (session["nurse_id"],)
    ).fetchone()
    return jsonify({
        "session_id": new_session["id"],
        "resumed": False,
        "cases_completed": 0,
        "total_cases": len(CASES)
    })

@app.route("/api/session/<int:session_id>/next_case")
@login_required
def next_case(session_id):
    db = get_db()

    # Verify session belongs to this nurse
    sim_session = db.execute(
        "SELECT * FROM sim_sessions WHERE id=? AND nurse_id=?",
        (session_id, session["nurse_id"])
    ).fetchone()
    if not sim_session:
        return jsonify({"error": "Session not found"}), 404
    if sim_session["completed_at"]:
        return jsonify({"done": True, "message": "Session already completed"})

    # Which cases have been answered in this session?
    answered_ids = {
        row["case_id"] for row in
        db.execute("SELECT case_id FROM responses WHERE session_id=?", (session_id,)).fetchall()
    }

    # Get this nurse's arm and case sequences
    nurse = db.execute("SELECT * FROM nurses WHERE id=?", (session["nurse_id"],)).fetchone()
    arm_seq  = json.loads(nurse["arm_sequence"])
    case_seq_raw = nurse["case_sequence"]
    # Fall back to default order for nurses registered before randomization was added
    case_seq = json.loads(case_seq_raw) if case_seq_raw else [c["id"] for c in CASES]

    # Present cases in this nurse's randomized (but fixed) order
    for idx, case_id in enumerate(case_seq):
        if case_id not in answered_ids:
            case = get_case_by_id(case_id)
            if not case:
                continue
            arm = arm_seq[idx] if idx < len(arm_seq) else "A"
            case_order = len(answered_ids) + 1

            # Build the response — redact ai_esi for arm A (will be revealed post-submission)
            payload = {
                "case_id": case["id"],
                "case_order": case_order,
                "total_cases": len(CASES),
                "arm": arm,
                "title": case["title"],
                "patient": case["patient"],
                "chief_complaint": case["chief_complaint"],
                "vitals": case["vitals"],
                "category": case["category"],
                "difficulty": case["difficulty"],
                "tags": case["tags"]
            }
            # Arm B: include AI recommendation upfront
            if arm == "B":
                payload["ai_esi"] = case["ai_esi"]
                payload["ai_rationale_preview"] = (
                    "AI triage support system recommends ESI " + str(case["ai_esi"])
                )
            return jsonify(payload)

    # All cases answered — mark session complete
    db.execute(
        "UPDATE sim_sessions SET completed_at=?, cases_completed=? WHERE id=?",
        (datetime.utcnow().isoformat(), len(CASES), session_id)
    )
    db.commit()
    return jsonify({"done": True})

# ─── Routes: Chat ──────────────────────────────────────────────────────────────

@app.route("/api/session/<int:session_id>/chat", methods=["POST"])
@login_required
def chat(session_id):
    """
    Process a nurse chat message. Returns scripted response from case data.
    Logs both the nurse message and system response to chat_messages.
    """
    db = get_db()
    data       = request.get_json()
    case_id    = data.get("case_id")
    message    = (data.get("message") or "").strip()
    elapsed_ms = data.get("elapsed_ms", 0)
    case_order = data.get("case_order")
    arm        = data.get("arm")

    if not case_id or not message:
        return jsonify({"error": "Missing required fields"}), 400

    case = get_case_by_id(case_id)
    if not case:
        return jsonify({"error": "Case not found"}), 404

    # Count existing messages for this case
    msg_count = db.execute(
        "SELECT COUNT(*) as n FROM chat_messages WHERE session_id=? AND case_id=? AND nurse_id=?",
        (session_id, case_id, session["nurse_id"])
    ).fetchone()["n"]

    intent = detect_intent(message)
    chat_responses = case.get("chat_responses", {})

    if intent in chat_responses:
        response_text = chat_responses[intent]
        section = intent
    else:
        response_text = chat_responses.get("unknown",
            "I can provide information about vitals, general appearance, respiratory status, "
            "neurological status, skin findings, cardiac findings, abdominal findings, "
            "history of present illness, past medical history, medications, allergies, "
            "pain assessment, or interventions already performed. What would you like to know?")
        section = "unknown"

    nurse_idx = msg_count + 1
    system_idx = msg_count + 2

    # Log nurse message
    db.execute(
        """INSERT INTO chat_messages
           (nurse_id, session_id, case_id, case_order, arm,
            sender, content, intent, section, message_index, elapsed_ms)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (session["nurse_id"], session_id, case_id, case_order, arm,
         "nurse", message, intent, section, nurse_idx, elapsed_ms)
    )
    # Log system response
    db.execute(
        """INSERT INTO chat_messages
           (nurse_id, session_id, case_id, case_order, arm,
            sender, content, intent, section, message_index, elapsed_ms)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (session["nurse_id"], session_id, case_id, case_order, arm,
         "system", response_text, intent, section, system_idx, elapsed_ms)
    )

    # Update or create partial response row for n_chat_messages tracking
    existing = db.execute(
        "SELECT * FROM responses WHERE session_id=? AND case_id=? AND nurse_id=?",
        (session_id, case_id, session["nurse_id"])
    ).fetchone()

    if not existing:
        db.execute(
            """INSERT INTO responses
               (nurse_id, session_id, case_id, case_order, arm,
                correct_esi, ai_esi, ai_correct, n_chat_messages, first_intent)
               VALUES (?,?,?,?,?,?,?,?,1,?)""",
            (session["nurse_id"], session_id, case_id, case_order, arm,
             case["esi"], case["ai_esi"], 1 if case["ai_correct"] else 0, intent)
        )
    else:
        # Update message count and unique intents
        current_intents = json.loads(existing["unique_intents_asked"] or "[]")
        if intent not in current_intents and intent != "unknown":
            current_intents.append(intent)
        db.execute(
            """UPDATE responses SET
               n_chat_messages = n_chat_messages + 1,
               unique_intents_asked = ?
               WHERE session_id=? AND case_id=? AND nurse_id=?""",
            (json.dumps(current_intents), session_id, case_id, session["nurse_id"])
        )

    db.commit()
    return jsonify({
        "intent": intent,
        "section": section,
        "response": response_text,
        "message_index": system_idx
    })

# ─── Routes: Response submission ───────────────────────────────────────────────

@app.route("/api/session/<int:session_id>/submit_initial", methods=["POST"])
@login_required
def submit_initial(session_id):
    """
    Submit the nurse's initial ESI choice (and confidence).
    For Arm A: returns the AI recommendation (held back until now).
    For Arm B: returns feedback immediately (no revision step).
    """
    db = get_db()
    sim_session = db.execute(
        "SELECT * FROM sim_sessions WHERE id=? AND nurse_id=?",
        (session_id, session["nurse_id"])
    ).fetchone()
    if not sim_session:
        return jsonify({"error": "Session not found"}), 404

    data               = request.get_json()
    case_id            = data.get("case_id")
    arm                = data.get("arm")
    initial_esi        = data.get("initial_esi")
    confidence         = data.get("initial_confidence")
    response_ms        = data.get("response_time_ms")
    case_order         = data.get("case_order")
    reasoning          = data.get("free_text_reasoning", "")
    working_hypothesis = data.get("working_hypothesis", "")
    cue_salience       = json.dumps(data.get("cue_salience", []))

    if not case_id or not initial_esi or not arm:
        return jsonify({"error": "Missing required fields"}), 400

    case = get_case_by_id(case_id)
    if not case:
        return jsonify({"error": "Case not found"}), 404

    # Check for existing row (may have been pre-created by chat)
    existing = db.execute(
        "SELECT * FROM responses WHERE session_id=? AND case_id=? AND nurse_id=?",
        (session_id, case_id, session["nurse_id"])
    ).fetchone()

    # If initial_esi already set, it was already submitted
    if existing and existing["initial_esi"] is not None:
        return jsonify({"error": "Already submitted for this case"}), 409

    initial_correct = 1 if initial_esi == case["esi"] else 0

    if arm == "B":
        # Final answer is initial answer; no revision phase
        if existing:
            # Update the pre-created row
            db.execute(
                """UPDATE responses SET
                   initial_esi=?, initial_confidence=?, final_esi=?, final_confidence=?,
                   initial_correct=?, final_correct=?,
                   changed_after_ai=0, direction_of_change='none',
                   response_time_ms=?, free_text_reasoning=?,
                   working_hypothesis=?, cue_salience=?
                   WHERE session_id=? AND case_id=? AND nurse_id=?""",
                (initial_esi, confidence, initial_esi, confidence,
                 initial_correct, initial_correct,
                 response_ms, reasoning, working_hypothesis, cue_salience,
                 session_id, case_id, session["nurse_id"])
            )
        else:
            db.execute(
                """INSERT INTO responses
                   (nurse_id, session_id, case_id, case_order, arm,
                    initial_esi, initial_confidence, final_esi, final_confidence,
                    correct_esi, ai_esi, ai_correct, initial_correct, final_correct,
                    changed_after_ai, direction_of_change, response_time_ms, free_text_reasoning,
                    working_hypothesis, cue_salience)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (session["nurse_id"], session_id, case_id, case_order, arm,
                 initial_esi, confidence, initial_esi, confidence,
                 case["esi"], case["ai_esi"], 1 if case["ai_correct"] else 0,
                 initial_correct, initial_correct,
                 0, "none", response_ms, reasoning, working_hypothesis, cue_salience)
            )
        db.commit()
        return jsonify({
            "arm": "B",
            "phase": "feedback",
            "initial_esi": initial_esi,
            "correct_esi": case["esi"],
            "ai_esi": case["ai_esi"],
            "ai_correct": case["ai_correct"],
            "initial_correct": bool(initial_correct),
            "correct_esi_rationale": case["correct_esi_rationale"],
            "ai_rationale": case["ai_rationale"],
            "teaching_point": case["teaching_point"]
        })
    else:
        # Arm A: store initial answer, return AI recommendation
        if existing:
            db.execute(
                """UPDATE responses SET
                   initial_esi=?, initial_confidence=?,
                   initial_correct=?, response_time_ms=?, free_text_reasoning=?,
                   working_hypothesis=?, cue_salience=?
                   WHERE session_id=? AND case_id=? AND nurse_id=?""",
                (initial_esi, confidence, initial_correct, response_ms, reasoning,
                 working_hypothesis, cue_salience,
                 session_id, case_id, session["nurse_id"])
            )
        else:
            db.execute(
                """INSERT INTO responses
                   (nurse_id, session_id, case_id, case_order, arm,
                    initial_esi, initial_confidence,
                    correct_esi, ai_esi, ai_correct, initial_correct,
                    response_time_ms, free_text_reasoning,
                    working_hypothesis, cue_salience)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (session["nurse_id"], session_id, case_id, case_order, arm,
                 initial_esi, confidence,
                 case["esi"], case["ai_esi"], 1 if case["ai_correct"] else 0,
                 initial_correct, response_ms, reasoning,
                 working_hypothesis, cue_salience)
            )
        db.commit()
        return jsonify({
            "arm": "A",
            "phase": "revision",
            "initial_esi": initial_esi,
            "ai_esi": case["ai_esi"],
            "ai_rationale_preview": "AI triage support system recommends ESI " + str(case["ai_esi"]),
            "initial_correct": bool(initial_correct)
        })

@app.route("/api/session/<int:session_id>/submit_revision", methods=["POST"])
@login_required
def submit_revision(session_id):
    """Arm A only: nurse may revise (or confirm) ESI after seeing AI recommendation."""
    db = get_db()
    data          = request.get_json()
    case_id       = data.get("case_id")
    final_esi     = data.get("final_esi")
    final_conf    = data.get("final_confidence")
    revision_ms   = data.get("revision_time_ms")

    if not case_id or not final_esi:
        return jsonify({"error": "Missing required fields"}), 400

    case = get_case_by_id(case_id)
    if not case:
        return jsonify({"error": "Case not found"}), 404

    row = db.execute(
        "SELECT * FROM responses WHERE session_id=? AND case_id=? AND nurse_id=?",
        (session_id, case_id, session["nurse_id"])
    ).fetchone()
    if not row:
        return jsonify({"error": "Initial submission not found"}), 404

    initial_esi    = row["initial_esi"]
    changed        = 1 if final_esi != initial_esi else 0
    if final_esi > initial_esi:
        direction = "higher"
    elif final_esi < initial_esi:
        direction = "lower"
    else:
        direction = "none"

    final_correct = 1 if final_esi == case["esi"] else 0

    db.execute(
        """UPDATE responses SET
           final_esi=?, final_confidence=?, final_correct=?,
           changed_after_ai=?, direction_of_change=?, revision_time_ms=?
           WHERE session_id=? AND case_id=? AND nurse_id=?""",
        (final_esi, final_conf, final_correct,
         changed, direction, revision_ms,
         session_id, case_id, session["nurse_id"])
    )
    db.commit()
    return jsonify({
        "arm": "A",
        "phase": "feedback",
        "initial_esi": initial_esi,
        "final_esi": final_esi,
        "correct_esi": case["esi"],
        "ai_esi": case["ai_esi"],
        "ai_correct": case["ai_correct"],
        "initial_correct": bool(row["initial_correct"]),
        "final_correct": bool(final_correct),
        "changed_after_ai": bool(changed),
        "direction_of_change": direction,
        "correct_esi_rationale": case["correct_esi_rationale"],
        "ai_rationale": case["ai_rationale"],
        "teaching_point": case["teaching_point"]
    })

@app.route("/api/session/<int:session_id>/ai_influence", methods=["POST"])
@login_required
def record_ai_influence(session_id):
    """Record whether the AI recommendation changed the nurse's thinking (both arms)."""
    db   = get_db()
    data = request.get_json()
    case_id     = data.get("case_id")
    ai_influence = data.get("ai_influence")
    if not case_id or ai_influence not in ("yes", "partially", "no"):
        return jsonify({"error": "Invalid payload"}), 400
    db.execute(
        "UPDATE responses SET ai_influence=? WHERE session_id=? AND case_id=? AND nurse_id=?",
        (ai_influence, session_id, case_id, session["nurse_id"])
    )
    db.commit()
    return jsonify({"ok": True})

# ─── Routes: Progress ──────────────────────────────────────────────────────────

@app.route("/api/session/<int:session_id>/progress")
@login_required
def session_progress(session_id):
    db = get_db()
    responses = db.execute(
        "SELECT * FROM responses WHERE session_id=? AND nurse_id=? ORDER BY case_order",
        (session_id, session["nurse_id"])
    ).fetchall()
    results = []
    for r in responses:
        results.append({
            "case_order": r["case_order"],
            "case_id": r["case_id"],
            "arm": r["arm"],
            "initial_esi": r["initial_esi"],
            "final_esi": r["final_esi"],
            "correct_esi": r["correct_esi"],
            "ai_esi": r["ai_esi"],
            "initial_correct": bool(r["initial_correct"]),
            "final_correct": bool(r["final_correct"]) if r["final_correct"] is not None else bool(r["initial_correct"]),
            "changed_after_ai": bool(r["changed_after_ai"]) if r["changed_after_ai"] is not None else False
        })
    return jsonify({
        "cases_completed": len(results),
        "total_cases": len(CASES),
        "results": results
    })

@app.route("/api/session/<int:session_id>/summary")
@login_required
def session_summary(session_id):
    db = get_db()
    rows = db.execute(
        "SELECT * FROM responses WHERE session_id=? AND nurse_id=?",
        (session_id, session["nurse_id"])
    ).fetchall()

    arm_a = [r for r in rows if r["arm"] == "A"]
    arm_b = [r for r in rows if r["arm"] == "B"]

    def accuracy(subset, field="final_correct"):
        if not subset:
            return None
        scored = [r[field] for r in subset if r[field] is not None]
        if not scored:
            return None
        return round(sum(scored) / len(scored) * 100, 1)

    baseline_acc = accuracy([r for r in arm_a if r["initial_correct"] is not None], "initial_correct")
    final_a_acc  = accuracy(arm_a, "final_correct")
    arm_b_acc    = accuracy(arm_b, "final_correct")

    changes      = [r for r in arm_a if r["changed_after_ai"]]
    n_changed    = len(changes)
    n_improved   = sum(1 for r in changes if r["final_correct"] and not r["initial_correct"])
    n_worsened   = sum(1 for r in changes if not r["final_correct"] and r["initial_correct"])

    return jsonify({
        "session_id": session_id,
        "total_cases": len(rows),
        "arm_a": {
            "n": len(arm_a),
            "baseline_accuracy_pct": baseline_acc,
            "post_ai_accuracy_pct": final_a_acc,
            "n_revised": n_changed,
            "n_improved_by_ai": n_improved,
            "n_worsened_by_ai": n_worsened
        },
        "arm_b": {
            "n": len(arm_b),
            "accuracy_pct": arm_b_acc
        }
    })

# ─── Routes: Admin ────────────────────────────────────────────────────────────

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    if data.get("password") == ADMIN_PASSWORD:
        session["is_admin"] = True
        session["username"] = "admin"
        return jsonify({"ok": True})
    return jsonify({"error": "Wrong password"}), 401

@app.route("/api/admin/nurses")
@admin_required
def admin_nurses():
    db = get_db()
    nurses = db.execute(
        "SELECT id, username, years_experience, role, work_setting, created_at FROM nurses ORDER BY created_at DESC"
    ).fetchall()
    return jsonify([dict(n) for n in nurses])

@app.route("/api/admin/nurse/<int:nurse_id>/reset", methods=["DELETE"])
@admin_required
def admin_reset_nurse(nurse_id):
    """Delete all responses and sessions for a nurse so their data is excluded from analysis."""
    db = get_db()
    if not db.execute("SELECT id FROM nurses WHERE id=?", (nurse_id,)).fetchone():
        return jsonify({"error": "Nurse not found"}), 404
    db.execute("DELETE FROM responses WHERE nurse_id=?", (nurse_id,))
    db.execute("DELETE FROM chat_messages WHERE nurse_id=?", (nurse_id,))
    db.execute("DELETE FROM sim_sessions WHERE nurse_id=?", (nurse_id,))
    db.commit()
    return jsonify({"ok": True})

@app.route("/api/admin/export/responses")
@admin_required
def export_responses():
    db = get_db()
    rows = db.execute("""
        SELECT
            n.username,
            n.years_experience,
            n.role,
            n.work_setting,
            r.session_id,
            r.case_id,
            r.case_order,
            r.arm,
            r.initial_esi,
            r.initial_confidence,
            r.final_esi,
            r.final_confidence,
            r.correct_esi,
            r.ai_esi,
            r.ai_correct,
            r.initial_correct,
            r.final_correct,
            r.changed_after_ai,
            r.direction_of_change,
            r.response_time_ms,
            r.revision_time_ms,
            r.sections_revealed_count,
            r.revealed_hpi,
            r.revealed_exam,
            r.revealed_pmh,
            r.hpi_reveal_ms,
            r.exam_reveal_ms,
            r.pmh_reveal_ms,
            r.info_seeking_log,
            r.free_text_reasoning,
            r.n_chat_messages,
            r.unique_intents_asked,
            r.first_intent,
            r.working_hypothesis,
            r.cue_salience,
            r.timestamp
        FROM responses r
        JOIN nurses n ON r.nurse_id = n.id
        ORDER BY r.session_id, r.case_order
    """).fetchall()

    si = io.StringIO()
    writer = csv.DictWriter(si, fieldnames=[
        "username","years_experience","role","work_setting",
        "session_id","case_id","case_order","arm",
        "initial_esi","initial_confidence","final_esi","final_confidence",
        "correct_esi","ai_esi","ai_correct","initial_correct","final_correct",
        "changed_after_ai","direction_of_change",
        "response_time_ms","revision_time_ms",
        "sections_revealed_count","revealed_hpi","revealed_exam","revealed_pmh",
        "hpi_reveal_ms","exam_reveal_ms","pmh_reveal_ms",
        "info_seeking_log","free_text_reasoning",
        "n_chat_messages","unique_intents_asked","first_intent",
        "working_hypothesis","cue_salience","ai_influence",
        "timestamp"
    ])
    writer.writeheader()
    for row in rows:
        writer.writerow(dict(row))

    output = io.BytesIO()
    output.write(si.getvalue().encode("utf-8-sig"))
    output.seek(0)
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"triage_responses_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    )

@app.route("/api/admin/export/chat")
@admin_required
def export_chat():
    """Full chat log — one row per message."""
    db = get_db()
    rows = db.execute("""
        SELECT
            n.username, n.role, n.years_experience,
            c.session_id, c.case_id, c.case_order, c.arm,
            c.sender, c.content, c.intent, c.section,
            c.message_index, c.elapsed_ms, c.timestamp
        FROM chat_messages c
        JOIN nurses n ON c.nurse_id = n.id
        ORDER BY c.session_id, c.case_order, c.message_index
    """).fetchall()

    si = io.StringIO()
    writer = csv.DictWriter(si, fieldnames=[
        "username","role","years_experience",
        "session_id","case_id","case_order","arm",
        "sender","content","intent","section",
        "message_index","elapsed_ms","timestamp"
    ])
    writer.writeheader()
    for row in rows:
        writer.writerow(dict(row))

    output = io.BytesIO()
    output.write(si.getvalue().encode("utf-8-sig"))
    output.seek(0)
    return send_file(
        output, mimetype="text/csv", as_attachment=True,
        download_name=f"triage_chat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    )

@app.route("/api/admin/export/summary")
@admin_required
def export_summary():
    """Per-nurse aggregate statistics."""
    db = get_db()
    nurses = db.execute("SELECT id, username, years_experience, role, work_setting FROM nurses").fetchall()
    rows_out = []
    for n in nurses:
        rows = db.execute(
            "SELECT * FROM responses WHERE nurse_id=?", (n["id"],)
        ).fetchall()
        if not rows:
            continue
        arm_a = [r for r in rows if r["arm"] == "A"]
        arm_b = [r for r in rows if r["arm"] == "B"]

        def acc(subset, field):
            vals = [r[field] for r in subset if r[field] is not None]
            return round(sum(vals)/len(vals)*100, 1) if vals else None

        rows_out.append({
            "username": n["username"],
            "years_experience": n["years_experience"],
            "role": n["role"],
            "work_setting": n["work_setting"],
            "n_responses": len(rows),
            "n_arm_a": len(arm_a),
            "n_arm_b": len(arm_b),
            "arm_a_baseline_acc": acc(arm_a, "initial_correct"),
            "arm_a_post_ai_acc":  acc(arm_a, "final_correct"),
            "arm_b_acc":          acc(arm_b, "final_correct"),
            "n_revised_arm_a":    sum(1 for r in arm_a if r["changed_after_ai"]),
            "n_improved_arm_a":   sum(1 for r in arm_a if r["changed_after_ai"] and r["final_correct"] and not r["initial_correct"]),
            "n_worsened_arm_a":   sum(1 for r in arm_a if r["changed_after_ai"] and not r["final_correct"] and r["initial_correct"]),
        })

    si = io.StringIO()
    if rows_out:
        writer = csv.DictWriter(si, fieldnames=list(rows_out[0].keys()))
        writer.writeheader()
        writer.writerows(rows_out)

    output = io.BytesIO()
    output.write(si.getvalue().encode("utf-8-sig"))
    output.seek(0)
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"triage_summary_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    )

@app.route("/api/admin/stats")
@admin_required
def admin_stats():
    db = get_db()
    n_nurses    = db.execute("SELECT COUNT(*) as n FROM nurses").fetchone()["n"]
    n_responses = db.execute("SELECT COUNT(*) as n FROM responses").fetchone()["n"]
    n_sessions  = db.execute("SELECT COUNT(*) as n FROM sim_sessions").fetchone()["n"]
    n_complete  = db.execute("SELECT COUNT(*) as n FROM sim_sessions WHERE completed_at IS NOT NULL").fetchone()["n"]

    # Completion funnel: nurses by how many cases they completed
    n_started   = db.execute(
        "SELECT COUNT(DISTINCT nurse_id) as n FROM responses"
    ).fetchone()["n"]
    n_reached_10 = db.execute(
        "SELECT COUNT(*) as n FROM (SELECT nurse_id FROM responses GROUP BY nurse_id HAVING COUNT(*) >= 10)"
    ).fetchone()["n"]
    n_completed_all = db.execute(
        "SELECT COUNT(*) as n FROM (SELECT nurse_id FROM responses GROUP BY nurse_id HAVING COUNT(*) >= 20)"
    ).fetchone()["n"]

    # Per-case completion: how many responses exist for each case_order position
    per_case_rows = db.execute(
        "SELECT case_order, COUNT(*) as n FROM responses WHERE case_order IS NOT NULL GROUP BY case_order ORDER BY case_order"
    ).fetchall()
    per_case = [{"case_order": r["case_order"], "n": r["n"]} for r in per_case_rows]

    return jsonify({
        "n_nurses": n_nurses,
        "n_responses": n_responses,
        "n_sessions": n_sessions,
        "n_completed_sessions": n_complete,
        "n_started": n_started,
        "n_reached_10": n_reached_10,
        "n_completed_all": n_completed_all,
        "per_case_completion": per_case
    })

# ─── Boot ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    load_cases()
    init_db()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print(f"\n  Triage Sim running on http://localhost:{port}")
    print(f"  Admin password: {ADMIN_PASSWORD}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
