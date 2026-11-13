# TeachBack: evaluation and teacher report (build brief)

This brief covers one part of TeachBack: turning a finished session into a teacher report. It assumes you have the product spec (`TeachBack_AI_Product_Spec_v1.1.md`) and are building the rest of the app (voice, whiteboard, Pip). Where this brief and the spec differ, this brief wins for the hackathon build, because it is cut down to what the 2-minute demo needs.

## What to build

When a session ends, one model call grades the session against a fixed checklist (the rubric), plain code checks and counts the result, and a report page shows it to a teacher.

```
session log  ─┐
              ├─> model call (evaluator prompt) ─> code checks ─> report JSON ─> report page
rubric.json  ─┘
```

There is no per-turn evaluation, no database, no hint ladder, and no transfer challenge in the demo. The evaluator runs once, at the end.

## Files in this folder

| File | What it is | What to do with it |
|---|---|---|
| `demo_script.md` | The timed 2-minute demo, with exact lines | The whole app must be able to play this |
| `rubric.json` | The checklist for the fractions lesson: 3 objectives, 3 misconceptions | Load as is. Written by a person; the model must not change it |
| `evaluator_prompt.md` | The full prompt for the evaluator model call | Use as is. Fill `{rubric}` and `{transcript}` |
| `sample_transcript.json` | A session log in the required format (the demo session) | The format the app must save. Also the test input |
| `sample_report.json` | A hand-written sample report for the demo session | The format the evaluator must output. Also the expected result for test 1 |
| `report.html` | The teacher report page, one file, no dependencies. The sample report is built in | Serve it, or port it to a React component |

## 1. Save the session log

During the session, append every turn to a list and keep it in memory. At the end it must look like `sample_transcript.json`:

```json
{
  "session_id": "sample_001",
  "topic_id": "fractions_compare_intro",
  "learner_name": "Sample learner (synthetic)",
  "started_at": "2026-11-13T15:00:00-08:00",
  "ended_at": "2026-11-13T15:01:20-08:00",
  "events": [
    { "id": "e1", "actor": "pip", "modality": "voice", "text": "I traded my one third..." },
    { "id": "e2", "actor": "learner", "modality": "voice", "text": "It doesn't matter. You both get one slice, so it's the same." },
    { "id": "e4", "actor": "pip", "modality": "whiteboard", "text": "Drew two pizzas of the same size: one cut into 3 equal slices, one cut into 4 equal slices." },
    { "id": "e5", "actor": "learner", "modality": "sketch", "text": "Circled one slice of the thirds pizza and one slice of the fourths pizza by hand." }
  ],
  "hints": [],
  "transfer": null
}
```

- `actor` is `learner` or `pip`. This field decides what counts as evidence, so it must be right.
- `modality` is `voice`, `text`, `sketch`, or `whiteboard`.
- Learner `voice` events hold the speech-to-text transcript, unedited.
- Learner `sketch` events hold the vision model's description of what the learner drew.
- Pip `whiteboard` events hold a one-line description of what Pip drew.
- `id` values are unique strings. They do not need to be consecutive.
- `hints` and `transfer` stay `[]` and `null` in the demo.

## 2. Call the evaluator

One function or endpoint, for example `POST /api/sessions/{id}/evaluate`:

1. Read `evaluator_prompt.md`. Replace `{rubric}` with the contents of `rubric.json` and `{transcript}` with the session log JSON. Use plain string replacement, not a format function: the prompt contains literal `{` and `}` in its JSON example.
2. Send it as one message to a fast model with temperature 0 and JSON output mode if the provider has one.
3. Parse the JSON from the reply. If parsing fails, retry once.

The reply has `outcome`, `summary`, `objectives`, `misconceptions`, `transfer`, and `next_steps`. The exact shape is at the bottom of `evaluator_prompt.md`.

## 3. Check and complete the result in code

Do not show the model's reply directly. Build the final report from it with these steps. This is what lets us say the AI cannot inflate its own grading.

1. **Objectives.** Keep only objectives whose `id` is in `rubric.json`. Add any rubric objective the model left out, with `before` and `after` set to `not_observed`. Copy each `label` from the rubric. Output them in rubric order.
2. **Misconceptions.** Keep only misconceptions whose `id` is in `rubric.json`. Copy each `label` from the rubric.
3. **Quotes.** Every `quote` and `resolution_quote` must appear inside the `text` of a learner event (compare after lowercasing, collapsing whitespace, and straightening curly quotes). If an objective's quote fails, set it to null. If a misconception's `quote` fails, drop that misconception. If its `resolution_quote` fails, set `resolved` to false and the quote to null.
4. **Outcome.** Recompute it; ignore the model's value.
   - `mastery_demonstrated`: every objective's `after` is `demonstrated_independent` or `demonstrated_assisted`, every misconception is resolved, and `transfer.attempted` and `transfer.passed` are true with no hints used.
   - `more_evidence_needed`: more than half of the objectives have `after` equal to `not_observed`.
   - `developing`: everything else.
5. **Session block.** Add `session`: `learner_name` from the log, `topic` from the rubric `title`, `date`, `duration_seconds` from `started_at` and `ended_at`, and `hint_count` from the length of `hints`.
6. Set `"sample": false`.

The final object has the same shape as the one in `sample_report.json`. The counts on the report page ("0 → 2 of 3 ideas explained", "1 of 1 misconceptions corrected") are computed by the page from this object, so they need no extra work.

## 4. Show the report

`report.html` renders the report with no build step. Serve it and open `report.html?src=/api/sessions/{id}/report`, where that URL returns the final report JSON. Opened with no `?src=`, or if the fetch fails, it shows the built-in sample, which is labelled as a sample on the page.

If you port it to React instead, keep the sections and wording: verdict, the four numbers, "What the student could explain" with before → after and the quote, "Misconceptions" with both quotes, and "What to do next". All text from the model must be escaped, as the page does now.

## 5. Timing for the demo

In `demo_script.md` the learner's last line is at about 0:53 and the report must be open at 1:30.

- Start the evaluator as soon as the learner's last line is transcribed, or from an "End session" button pressed at that moment. Pip's closing line plays while it runs.
- The call should return in under 10 seconds. Use a fast model and keep the single call.
- Show the report automatically when it is ready, or via one click.

## Rules that must hold

1. Only `learner` events are evidence. Pip's words and drawings never raise an objective's status.
2. A right answer with no reason is `partial`, not demonstrated.
3. A misconception is `resolved` only if the learner later states the correct idea.
4. No quote appears in the report unless it is in the log.
5. The outcome and all counts come from code, not from the model.
6. If `sample` is true, the page says so. Never present the sample as a live result.

## How to check it works

**Test 1: the demo session.** Run the evaluator on `sample_transcript.json`. Expected:

| Item | Expected |
|---|---|
| `more_parts_smaller` | `contradicted` → `demonstrated_independent` |
| `same_whole` | `not_observed` → `demonstrated_independent` |
| `denominator_meaning` | `not_observed` → `not_observed` |
| Misconception `same_numerator_equal` | present, quote from `e2`, resolved, resolution quote from `e10` |
| Outcome | `developing` |
| Page numbers | "0 → 2 of 3", "1 of 1", "Not tried", "0" |

`sample_report.json` is this expected result written by hand. Wording of `summary`, `note`, and `next_steps` will differ; statuses and quotes should match.

**Test 2: no correction.** Delete event `e10` from the log and run again. Expected: the misconception is "Still there", no objective is demonstrated, the page shows "0 → 0 of 3".

**Test 3: Pip says the right thing, the learner does not.** Replace `e10` with a Pip event carrying the same text. Expected: same result as test 2.

If test 3 fails, the evaluator is crediting the student for the AI's words, which is the one failure that breaks the product's claim.

## Fallback on stage

If the live evaluation fails or is slow, open `report.html` with no `?src=`. It shows the built-in sample, which is marked as a sample on the page; say so out loud.
