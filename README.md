# PedESI Triage Sim

Pediatric ESI triage simulation platform for nurse competency assessment and AI decision-support research.

## Setup

```bash
pip install flask
python app.py
# → http://localhost:5000
```

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | auto-generated | Flask session signing key — set a fixed value for persistence across restarts |
| `ADMIN_PASSWORD` | `triage_admin_2024` | Password for admin dashboard |
| `PORT` | `5000` | Server port |
| `FLASK_DEBUG` | `false` | Enable debug mode |

## Admin access

Navigate to login, use username `admin` and the admin password. Provides nurse roster, aggregate stats, and CSV exports.

## Data exports

- **Response CSV** — one row per nurse-case response; all fields for multilevel modeling
- **Summary CSV** — one row per nurse; aggregated accuracy metrics by arm

## Study design

Within-subject: each nurse is randomly assigned 10 Arm A cases and 10 Arm B cases (balanced, shuffled per nurse at registration).

- **Arm A (Baseline-first)**: nurse decides ESI → sees AI recommendation → may revise → feedback
- **Arm B (AI-first)**: nurse sees AI recommendation upfront → decides ESI → feedback

### Key outcome variables

| Variable | Notes |
|---|---|
| `initial_correct` | Nurse accuracy before AI exposure |
| `final_correct` | Nurse accuracy after AI (Arm A: post-revision; Arm B: same as initial) |
| `changed_after_ai` | Arm A: did nurse revise after AI reveal? |
| `direction_of_change` | higher / lower / none |
| `response_time_ms` | Time from case display to initial submission |
| `revision_time_ms` | Arm A: time from AI reveal to revision submission |

### Suggested additional data to collect (not yet implemented)

- Nurse fatigue/cognitive load (mid-session survey)
- Trust-in-AI self-report scale (post-session)
- Perceived AI accuracy estimate (post-session)
- Case-specific difficulty perception rating

## Case library

20 pediatric ED cases, ESI 1–5:

| ESI | n | AI Errors |
|---|---|---|
| 1 | 3 | 0 |
| 2 | 5 | 2 (Cases 4, 7 — undertriage; petechiae/fever, opioid toxidrome) |
| 3 | 6 | 2 (Cases 9, 13, 14 — undertriage; appendicitis, SVT, croup at rest) |
| 4 | 4 | 0 |
| 5 | 2 | 0 |

AI is intentionally incorrect on 5/20 cases (25%), all undertriage errors, to probe anchoring on unsafe AI recommendations.
