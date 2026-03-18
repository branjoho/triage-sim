# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
pip install flask
python app.py
# → http://localhost:5000
```

Key environment variables:
- `SECRET_KEY` — Flask session signing key (set a fixed value for persistence across restarts)
- `ADMIN_PASSWORD` — default `triage_admin_2024`
- `PORT` — default `5000`
- `FLASK_DEBUG` — default `false`

Admin login: username `admin` + admin password at `/login`.

## Architecture

**Single-file backend + single-file frontend.** All server logic lives in `app.py`; all UI lives in `templates/index.html` as a single-page app with JavaScript-driven page switching (no router library). `cases.json` holds the full case library.

**Database:** SQLite with WAL mode. Schema migrations run automatically on startup via `ALTER TABLE ... ADD COLUMN` (errors silently ignored for idempotency). Four tables:
- `nurses` — credentials, demographics, per-nurse `arm_sequence` and `case_sequence` (stored as JSON arrays)
- `sim_sessions` — one per simulation run, tracks completion
- `responses` — one row per nurse-case; primary outcome table for analysis
- `chat_messages` — one row per message for interaction analysis

## Study design implementation

Each nurse gets exactly 10 Arm A + 10 Arm B cases, shuffled (`generate_arm_sequence()`), with a randomized case order (`generate_case_sequence()`). Both sequences are generated at registration and stored in the DB so they persist across session resumptions.

**Arm A flow:** case loads without AI → nurse chats + submits initial ESI → AI recommendation revealed → nurse can revise → feedback shown
**Arm B flow:** AI recommendation injected into chat immediately on case load (500ms delay) → nurse chats + submits ESI → feedback shown (no revision phase)

The `responses` row can be pre-created by the chat endpoint (to capture intent data before submission). The submit endpoint updates or inserts to handle both paths.

## Chat / intent system

No generative AI — all responses are pre-scripted in `cases.json` under `chat_responses[intent]`. Intent detection is pure keyword scoring across 14 categories (vitals, appearance, respiratory, neuro, skin, cardiac, abdominal, hpi, onset, pmh, medications, allergies, pain, interventions). Unknown intents fall back to a generic response.

Timing is calculated client-side (`S.timerStart`) and sent to the backend as milliseconds: `response_time_ms` (case load → initial submit) and `revision_time_ms` (AI reveal → revision submit).

## Data exports (admin only)

- `/api/admin/export/responses` — one row per nurse-case; primary dataset for multilevel modeling
- `/api/admin/export/chat` — one row per message with intent/timing
- `/api/admin/export/summary` — per-nurse aggregated accuracy metrics
