# Design: Richer Chat Responses via Offline Claude Generation

**Date:** 2026-03-19
**Status:** Approved

## Overview

Replace the current hand-scripted `chat_responses` entries in `cases.json` with Claude-generated responses written in a natural caregiver/patient voice. A one-time offline generation script produces the new responses and writes them back to `cases.json`. No runtime API dependency is introduced. The intent detection and keyword matching logic in `app.py` is extended to cover 10 new categories.

## Problem

The current scripted responses have two issues:
1. **Robotic tone** — responses read as clinical notes, not as a parent or caregiver speaking to a nurse.
2. **High fallback rate** — nurses asking questions outside the 14 recognized intent categories receive a generic fallback response, breaking immersion.

## Approach

Offline generation (Option B): use the Claude API once to generate natural-language responses for all intent categories across all 20 cases. Store results in `cases.json`. Re-run the script if cases change.

This was chosen over live API integration to avoid runtime latency, runtime API cost, and response variability between participants (a study validity concern).

## Intent Categories

### Existing (14) — responses rewritten in caregiver voice

`vitals`, `appearance`, `respiratory`, `neuro`, `skin`, `cardiac`, `abdominal`, `hpi`, `onset`, `pmh`, `medications`, `allergies`, `pain`, `interventions`

### New (10) — added to reduce fallback rate

| Category | Covers |
|---|---|
| `hydration` | Fluid intake, wet diapers, tears, dry mouth |
| `fever_history` | Fever duration, antipyretic response, temperature trend |
| `behavior` | Activity level, irritability, interaction vs. baseline |
| `feeding` | Oral intake, nursing, appetite changes |
| `urinary` | Urine output frequency and color changes |
| `exposure` | Sick contacts, daycare, travel |
| `immunization` | Vaccine history, last immunizations |
| `family_history` | Relevant family medical history |
| `caregiver_concern` | What worries the caregiver most |
| `review_of_systems` | Systematic symptom review not captured by other intents |

**Note:** "How long ago did this start" is covered by the existing `onset` category — generation prompt explicitly instructs rich, case-specific onset responses.

### Fallback — made case-specific (key: `"unknown"`)

Claude generates a case-specific fallback response per case stored under the key `"unknown"` in `chat_responses`. This matches the existing `app.py` lookup: `chat_responses.get("unknown", <hardcoded string>)`. The fallback is not an intent category and must not be included in keyword mapping or intent logging logic.

## Generated JSON Structure

Claude returns a flat JSON object with exactly 25 keys per case: 24 intent categories + `"unknown"`. Example:

```json
{
  "vitals": "He felt really hot to me, I took his temp at home and it was 103...",
  "appearance": "He's just not himself, really pale and not wanting to be put down...",
  "hydration": "He's been refusing the bottle since this morning, maybe had two wet diapers today...",
  "unknown": "I'm sorry, I'm not sure what you mean — can you say that a different way?",
  ...
}
```

This flat dict is written directly as the `chat_responses` value for that case in `cases.json`.

## Generation Script

**File:** `generate_responses.py` (project root)

**Model:** `claude-opus-4-5-20250514` (pinned — re-generation against a different model version may produce different responses; re-pin and re-run if the model is deprecated)

**Batching:** One API call per case (20 calls total). This keeps each prompt within a manageable token budget and isolates failures per case.

**Rate limiting:** 0.5s sleep between calls to avoid hitting API rate limits.

**Inputs:**
- `cases.json` — source of clinical facts
- `ANTHROPIC_API_KEY` environment variable

### Per-case prompt: what to include

| Field | Include? | Reason |
|---|---|---|
| Demographics, weight, sex | Yes | Needed for age-appropriate persona |
| Chief complaint | Yes | Core context |
| Vitals | Yes | Needed for accurate responses |
| HPI | Yes | Caregiver would know this narrative |
| PMH | Yes | Caregiver would know this history |
| Exam | **No** | Objective clinician findings — caregiver would not know auscultation, pupils, etc. |
| `esi`, `ai_esi` | No | Blinded — core study validity requirement |
| `correct_esi_rationale`, `ai_rationale` | No | Blinded |

The `exam` field is withheld because it contains objective clinical observations (e.g., "diffuse crackles," "fixed and dilated pupils") that a caregiver at bedside would not report. If a nurse asks about something only knowable from the exam, the caregiver response should say "I don't know, you'd have to check."

### Persona rules

**Standard cases (parent/caregiver present):** "You are the parent or caregiver of this patient. You brought them to the ED. Respond naturally as you would speaking directly to an ED nurse. You do not know the medical severity of their condition."

**Patient-as-speaker (age ≥ 12):** "You are the patient. You are [age] years old. Respond naturally as you would speaking directly to an ED nurse. You do not know the medical severity of your condition."

**Non-verbal / critically ill / EMS-brought (e.g., GCS ≤ 8, apneic, or no parent present):** "You are the parent or caregiver. You may not know details of what happened after EMS arrived. Respond based only on what you witnessed before EMS. For clinical findings you could not observe, say 'I don't know, I wasn't there for that part.'"

The generation script determines persona type per case using:
- `age_years >= 12` → patient-as-speaker
- `vitals.gcs <= 8` OR case flagged as EMS-only → non-verbal/critical persona
- Otherwise → standard caregiver persona

### Error handling and validation

1. **Backup:** Script writes a timestamped backup of `cases.json` (e.g., `cases.json.bak.2026-03-19`) before making any changes.
2. **Per-case validation:** After receiving Claude's response, validate that the parsed JSON contains all 25 expected keys. If any key is missing, log a warning and skip writing that case (leave the original response intact).
3. **JSON parse failure:** If Claude returns malformed JSON, log the error and skip that case. Do not abort the entire run.
4. **Summary report:** After completion, print a summary: cases updated, cases skipped, and any failures.

## Keyword Mapping (app.py changes)

The intent scoring function in `app.py` is extended with keyword lists for the 10 new categories. Keyword conflicts with existing categories are resolved by specificity: more specific categories take priority via higher weights or by removing ambiguous terms from less-specific lists.

| Category | Keywords | Conflict resolution |
|---|---|---|
| `hydration` | drinking, fluids, tears, thirsty, intake, dry mouth | Remove "wet diapers" (overlap with `urinary`); "diapers" alone stays |
| `fever_history` | fever, how long fever, tylenol, motrin, antipyretic, temperature history | "temperature" removed (kept in `vitals`); "how long" scoped to fever context |
| `behavior` | acting, behavior, irritable, fussy, lethargic, playful, herself, himself | No significant overlaps |
| `feeding` | eating, feeding, nursing, appetite, bottle, solids, breastfeed | No significant overlaps |
| `urinary` | urine, urinating, pee, wet diapers, diaper count, output | "output" scoped to urinary context |
| `exposure` | sick contact, daycare, school, travel, exposed, contagious | No significant overlaps |
| `immunization` | up to date, immunized, last shot, vaccination record | Remove "vaccines", "immunizations", "shots" from `pmh` keyword list — these overlap directly and `pmh` would always win under tie-breaking rules |
| `family_history` | family history, hereditary, runs in the family | "mom/dad/sibling" removed (too generic) |
| `caregiver_concern` | worried about, most concerned, scared about, what do you think | No significant overlaps |
| `review_of_systems` | anything else, other symptoms, head to toe, overall, everything | No significant overlaps |

**Tie-breaking:** The existing scoring logic uses highest score wins, with ties broken by list order. The new categories are appended after existing ones in the scoring dict, so existing category keywords remain higher priority in true ties.

## Files Changed

| File | Change |
|---|---|
| `generate_responses.py` | New — offline generation script |
| `cases.json` | Updated — `chat_responses` rewritten + 10 new categories + case-specific `"unknown"` fallback |
| `app.py` | Updated — keyword lists for 10 new intent categories added to scoring function |

## Study Validity Notes

- `esi`, `ai_esi`, `correct_esi_rationale`, and `ai_rationale` are never passed to Claude during generation
- `exam` field is withheld — caregiver would not know objective clinical findings
- Claude is instructed per persona rules above — caregiver does not know medical severity
- Model is pinned (`claude-opus-4-5-20250514`) — re-generation will produce identical results on the same model
- Temperature 0.3 reduces response variance within a model version; note that changing the pinned model will produce different outputs
- All participants see the same pre-generated responses for a given case — no per-session variability

## Out of Scope

- Live/runtime Claude API integration (deferred — Option A)
- Changes to the ESI recommendation logic
- Changes to the study arm flow (Arm A / Arm B)
- UI changes to the chat interface
