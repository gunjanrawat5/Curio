# TeachBack AI

**Product requirements document, experience specification, and engineering blueprint**  
**Version:** 1.1  
**Status:** Hackathon MVP specification with expansion roadmap  
**Tagline:** *If you can teach it, you understand it.*

> **v1.1 revision notes**
> - **Flagship topic is now kid-friendly: Fractions** (comparing 1/3 and 1/4), chosen for the Epic audience (children ages 12 and under). Binary Search is kept as an optional advanced topic in Appendix A.
> - **Vision is now a real, required MVP moment:** the learner sketches freehand (for example, circling or shading a piece of a fraction bar), the app sends a canvas snapshot, and the AI student references what was actually drawn. See §4.4 Mode F and §6.4.
> - **The demo is trimmed to three beats** (the AI draws from your voice; the AI catches a gap or mistake and questions it; the report shows the transfer result with the eval number). The hint-ladder tour is cut from the demo but stays in the product. See §15.5.
> - **New: the evaluator “eval number”** (§16.5), a small scripted-transcript check that backs the report and the demo claim.

---

## 0. Executive summary

TeachBack AI is a multimodal learning application that reverses the conventional AI-tutor relationship. Instead of watching an AI explain a topic, **the learner must teach an AI student**. The AI student listens, asks genuine follow-up questions, expresses reasonable doubts, introduces carefully controlled misconceptions, and requests examples. The learner can answer through **natural voice conversation, typing, a shared editable whiteboard, or a combination of all three**.

The whiteboard is more than a drawing area. An **AI Whiteboard Copilot** can generate a diagram from a spoken request, add labels and arrows, highlight important elements, clean up rough sketches, and *propose* corrections when a drawing conflicts with the explanation. It performs edits using validated, structured drawing actions, not by painting over a flat image. The learner retains control of their work.

Behind the friendly AI student, an independent **Mastery Evaluator** compares the learner's explanations and challenge responses against a topic-specific rubric. It records evidence, misconceptions, revisions, hints, and independent performance. Completion requires evidence of understanding, not merely an agreeable conversational model saying “I get it.” At the end, the app produces a **personalized performance report** with demonstrated skills, gaps, concrete examples from the session, hints used, mistakes corrected, and recommended practice.

### One-sentence pitch

> TeachBack is an AI student you teach with your voice, text, and drawings; it challenges your reasoning, draws alongside you, and produces an evidence-backed report showing what you actually understand.

### The core loop

**Choose a topic → Explain → AI questions your reasoning → Draw / illustrate / refine → Address misconceptions → Solve an independent transfer challenge → Receive a mastery report.**

### Hard product decision: no webcam

The **learner-facing camera and facial-expression analysis are explicitly out of scope**. “Vision” in this product means the AI can inspect **the learner's own freehand sketches on the digital whiteboard** (sent as a canvas snapshot) alongside the structured diagram state, not the learner's face or surroundings. Hints may be triggered by a pause, a request for help, repeated unsuccessful attempts, or evaluation evidence—not by visual inferences about emotion.

---

## 1. The problem and opportunity

### 1.1 The learning problem

A learner can listen to explanations, read generated answers, or copy a solution while still being unable to explain why it works. Conventional educational chatbots often optimize for answering quickly. They can inadvertently substitute for the learner's reasoning, and they may overpraise an incomplete response.

TeachBack is built around the **learning-by-teaching** idea: expressing an explanation, justifying it, handling counterexamples, and applying the concept in a new context are stronger observable demonstrations of understanding than passively receiving an answer.

### 1.2 What users need

- A patient, responsive practice partner they can teach without social pressure.
- A conversation that probes *why*, not just *what*.
- Flexible expression: speech, sketches, text, and mixed input.
- Visual support without needing to manually create every box, label, pointer, or arrow.
- Feedback that differentiates a correct answer from a sound explanation.
- Hints that preserve the opportunity to think.
- A trustworthy summary of what was demonstrated, what remained uncertain, and what to practice next.

### 1.3 Product opportunity

The differentiator is the combination of **role reversal**, **active questioning**, **editable generative diagrams**, **independent evaluation**, and **evidence-based learning reports** in one tightly integrated experience.

### 1.4 Target users

**Initial persona — elementary-school student (about ages 8 to 12):** A child, often with a parent or teacher nearby, practicing a concept they have just been taught. Flagship example: comparing fractions. Other early topics: place value, the water cycle, and basic shapes.

**Secondary personas — later:** Teachers assigning “teach it back” exercises; parents supporting children; study groups; older learners and candidates practicing technical explanations (see Appendix A: Binary Search); learners with a preference for visual or spoken reasoning.

### 1.5 Product principles

1. **Learner does the thinking.** The AI prompts and scaffolds rather than routinely supplying the complete explanation.
2. **Ask before concluding mastery.** Understanding requires demonstrable evidence, ideally on a novel example.
3. **Visually useful, not visually noisy.** Whiteboard edits should clarify the explanation, not turn every sentence into an animation.
4. **Correctness and friendliness are separate.** The AI student may be warm while the evaluator remains rigorous.
5. **Preserve learner ownership.** User-created diagrams are never silently overwritten.
6. **Be transparent about assistance.** AI-generated diagrams and hint-assisted responses are labeled appropriately.
7. **Build for the demo, architect for expansion.** A small reliable set of topics and diagram primitives is preferable to unsupported claims of universal expertise.

---

## 2. Goals, non-goals, and success criteria

### 2.1 Product goals

- Enable fluid teaching sessions using **voice, typing, and drawing** interchangeably.
- Provide context-aware follow-up questions that challenge missing concepts and misconceptions.
- Let the AI **create, annotate, and propose edits** to structured whiteboard diagrams.
- Track progress against a **predefined topic rubric**.
- Escalate hints gradually when assistance is appropriate.
- Require an independent challenge before declaring mastery.
- Generate an actionable, evidence-backed session report.
- Deliver a cohesive and memorable **two-minute live demonstration**.

### 2.2 Non-goals for the hackathon MVP

- Webcam, facial-expression reading, gaze tracking, or emotion inference.
- Fully autonomous generation of arbitrary educational art or photorealistic illustrations.
- Reliably recognizing every kind of handwritten mathematical notation.
- Supporting every possible subject equally well.
- Integrating learning-management systems, classrooms, grading systems, or payments.
- Fine-tuning or retraining the base language model in response to each lesson.
- Treating AI “confidence” or friendliness as proof of learning.
- Advanced multi-user whiteboard collaboration.
- Building every component as an independent deployed agent or microservice.

### 2.3 Measurable MVP acceptance criteria

| Area | Minimum acceptable behavior | Strong demo target |
|---|---|---|
| Voice | Learner speaks and receives an audible contextual reply | Natural interruptions and concise follow-ups |
| Text | Typed explanations enter the same conversation | Seamless switching between typing and voice |
| Whiteboard | Learner can draw and add shapes/text | AI draws a fraction bar from speech and shades parts on request |
| Visual understanding | Model receives a snapshot of the learner's freehand sketch | Question references what the learner actually drew (for example, which piece they circled) |
| AI questioning | At least one question targets a missing objective | Questions adapt to the learner's latest actual answer |
| Hints | User can request a subtle hint | Progressive hint levels tracked in evidence |
| Evaluation | Objective statuses update from recorded responses | Detects a seeded misconception and confirms correction |
| Mastery | Independent final challenge with rubric-based pass/fail | Does not pass a deliberately wrong explanation |
| Report | Shows strengths, gaps, hints, and next step | Cites specific answer excerpts and whiteboard evidence |
| Evaluator accuracy | Runs on 10 scripted learner transcripts | At least 9 of 10 match human labels; never passes a planted-wrong explanation |
| Reliability | One full session works without manual database repair | Can complete the demo after a provider reconnect |

**Important:** The product can measure observable *performance in a session*; it should not claim scientifically validated long-term learning gains from one session alone.

---

## 3. End-to-end learner experience

### 3.1 User journey overview

```text
Landing / Welcome
    ↓
Choose Topic + Difficulty
    ↓
Meet the AI Student
    ↓
Explain with Voice / Text / Whiteboard
    ↓
AI Student Asks a Follow-up or Doubt
    ↓
Whiteboard Copilot Generates or Edits a Visual (if needed)
    ↓
Mastery Evaluator Records Evidence
    ├── Gap remains → More teaching / subtle hint / counterexample
    └── All key objectives demonstrated → Independent challenge
                                                ↓
                                        Pass / Retry / Needs practice
                                                ↓
                                      Personalized Session Report
```

### 3.2 Screen A: Landing / topic selection

**Primary message:** “Pick something you think you know. Teach it to an AI student.”

**Controls:**

- Topic input, e.g. `Fractions`.
- Suggested topic tiles for the MVP: `Fractions` (flagship) and, optionally, `Binary Search` as an advanced tile (Appendix A).
- Difficulty selector: Beginner / Intermediate / Advanced (can default to Beginner).
- Session goal: “Explain it well enough to teach it” (default).
- Start button: `Start teaching`.

**System behavior:**

- Load a canonical topic definition from a curated topic library when available.
- If the topic is unsupported in MVP, show a graceful message and suggest available topics instead of inventing an unvalidated rubric.
- Initialize an AI student persona and a clear evaluation rubric.

### 3.3 Screen B: Main teaching workspace

**Suggested layout:**

```text
┌─────────────────────────────────────────────────────────────────────┐
│ TeachBack         Topic: Fractions            Progress 2/4      ⋯   │
├─────────────────────────────────┬───────────────────────────────────┤
│                                 │  AI STUDENT (Pip)                 │
│          WHITEBOARD             │  Avatar + voice activity          │
│                                 │                                   │
│   1/3  ┌───┬───┬───┐            │  “Are those two pieces the        │
│        │███│   │   │            │   same size? They look            │
│        └───┴───┴───┘            │   different to me.”               │
│   1/4  ┌──┬──┬──┬──┐            │                                   │
│        │  │██│  │  │            │  Conversation / transcript        │
│        └──┴──┴──┴──┘            │                                   │
│                                 │  [Speak] [Type reply] [Hint]      │
│   Pen  Shade  Text  Erase       │                                   │
│   + AI Draw    Clean up         │                                   │
├─────────────────────────────────┴───────────────────────────────────┤
│ AI actions: “Drew two bars”   [Undo]   [Confirm suggestion]         │
└─────────────────────────────────────────────────────────────────────┘
```

**Whiteboard pane:**

- Freehand drawing and erasing.
- Shapes, arrows, and text labels.
- Pan/zoom as feasible.
- AI creation and annotation commands with a visible action history.
- Optional selection of a diagram region before requesting AI edits.

**Conversation pane:**

- AI avatar or simple audio-reactive visual; 2D is enough.
- Live or near-live user speech transcript.
- AI replies, follow-up questions, and hint requests.
- Text-entry fallback when audio is unavailable.
- Display when the AI is speaking, listening, processing a drawing, or waiting for a response.

**Learning progress element:**

- A small “Objectives demonstrated” indicator; don't display detailed grades every second.
- Optional expandable list of covered concepts to help users understand what remains.

### 3.4 Screen C: Independent challenge

When all required concepts are sufficiently supported, the AI student says something like:

> “I think I understand! Could you show me how this works on a different example, without my help?”

Challenge requirements:

- New input or scenario, not a verbatim repeat of the taught example.
- Learner explains both *what to do* and *why*.
- Hints are disabled for a “fully independent” pass, or help requests are recorded as assisted practice and lead to a fresh retry challenge.
- Evaluator checks explicit conditions and produces `passed`, `needs_retry`, or `incomplete`.

### 3.5 Screen D: Session report

Display a concise summary at the top, followed by evidence and recommendations. The report must distinguish observed performance from inferred mastery, identify which criteria remain unproven, and show the assistance used.

**Report sections:**

1. Topic and session metadata.
2. Outcome: Mastery demonstrated / Developing / More evidence needed.
3. Learning objectives and evidence statuses.
4. Conceptual strengths.
5. Misconceptions, corrections, and unresolved gaps.
6. Question performance and independent challenge outcome.
7. Hint usage by level.
8. Whiteboard contribution (student-created, AI-created, corrected, or co-created diagrams).
9. Personalized next practice task.
10. Optional short narrative summary for student/teacher.

---

## 4. Detailed feature requirements

### 4.1 Voice conversation

**Purpose:** Give the experience the feel of explaining a concept to another person.

**Behavior:**

- The learner can speak naturally and pause for thought.
- The AI student answers conversationally, preferably with streaming audio.
- The AI asks one primary question at a time.
- Allow interruption / “Actually, wait…” when the provider supports it; otherwise implement push-to-talk with clean turn boundaries.
- Keep utterances short enough not to monopolize the session.
- Preserve transcript segments as timestamped session events for downstream evaluation.
- AI student should refer to active drawings only after the canvas has been analyzed or the underlying structured diagram state is known.

**Critical interaction contract:** A spoken claim such as “those two pieces are the same size” is an assertion, **not automatically a fact**. It must be checked against the known diagram state (parts, denominators, shaded pieces) before the diagram is updated or the student is scored.

**Fallback:** If streaming voice fails, show a microphone reconnect control and allow text input. A successful hackathon demo must not require audio to be the sole interaction path.

### 4.2 Typed teaching

**Purpose:** Accessibility, code-heavy explanations, quiet environments, and continuity when microphone permissions fail.

**Behavior:**

- Typed explanations enter the same shared conversation history as speech.
- Text can reference current visual objects, e.g. “Point to the shaded piece.”
- The AI should not penalize an explanation because it was typed rather than spoken.
- Code snippets and mathematical notation should be preserved, not flattened unnecessarily.

### 4.3 Digital whiteboard

**Purpose:** Support spatial, procedural, and mathematical explanations.

**Expected drawing primitives for MVP:**

- Freehand pen and eraser (required: this is what the vision moment reads).
- Fraction bar divided into N equal parts.
- Shading of selected parts (by tap or by freehand fill).
- Number line with tick marks and a placed marker.
- Text and numbers (for example `1/3`).
- Line and arrow.
- Highlight and circle.
- Undo/redo.

**Stretch primitives:** Fraction circles, array cells with `L`/`R`/`mid` pointers and dimmed ranges (Appendix A), tree nodes, graph edges, coordinate axes, flowchart blocks, labels on arrows, simple animation across state changes.

**User-owned strokes vs AI elements:** Represent elements with stable IDs and ownership metadata. The system must be able to identify and undo AI-generated operations independently from user-created strokes.

### 4.4 AI Whiteboard Copilot

**Purpose:** Transform spoken/typed concepts into editable visuals and help refine existing visuals.

This is a **tool-using model role**, not necessarily another always-running voice session. The conversational model or orchestrator invokes it when a visual action is appropriate.

#### Mode A — Draw for me

User: “Let's compare one third and one fourth.”

System:

1. Detects that a diagram would help.
2. If no fractions were supplied, creates **clearly labeled illustrative fractions** (for example 1/3 and 1/4).
3. Sends structured `create_fraction_bar` commands to the frontend, giving both bars the **same whole width** so the comparison is fair.
4. Renders editable fraction bars, not a flat generated PNG.
5. Records `source: ai_generated_example`, so the AI's choices are not attributed to the learner.

**Guardrail:** If the user supplies fractions, preserve them exactly. Do not silently change the number of parts or swap in easier fractions.

#### Mode B — Annotate my explanation

User: “Shade one piece of each bar.”

System: Shades the requested part of each bar, provided the request is consistent with the diagram. If the request is ambiguous (“shade the big piece”), it asks which one.

#### Mode C — Fix / clean up my drawing

User: “Can you make my bars neat?”

System:

- Inspects current shapes and strokes.
- Proposes aligned bars and evenly sized parts.
- Shows a preview of the change when feasible.
- Requires confirmation before destructive replacement, because uneven parts may be the very misconception being taught.
- Preserves original strokes in undo history.

#### Mode D — Suggest a conceptual correction

User draws a bar with uneven pieces and calls them fourths.

System: “Your bar has 4 pieces, but they're different sizes. For fourths, they'd all need to match. Should I even them out?”

The drawing is **not silently corrected**, because the mismatch may be essential evidence of misunderstanding.

#### Mode E — Suggest a visual

AI student: “Would it help if I lined the two bars up so we can compare the pieces?”

User can accept or decline; repeated unsolicited visuals should be avoided.

#### Mode F — Read the learner's sketch (required vision moment)

This mode is the MVP's real use of vision. Structured diagram state already tells the system what the **AI** drew; a freehand stroke carries no structure, so the **snapshot is the only way to know what the learner drew by hand**.

Flow:

1. The learner draws by hand (circles or shades a piece, or sketches their own bar) and says what it means.
2. After a short pause, or when the learner taps “Show Pip,” the app exports a canvas snapshot together with the structured diagram state and the canvas revision. Debounce so a stroke in progress is never analyzed.
3. The Vision Analyzer (§6.4) returns structured observations with confidence: which element, which part, and what kind of mark.
4. If confidence is low or the reference is ambiguous, the AI student asks (“Did you circle the piece in the top bar or the bottom bar?”) instead of asserting.
5. Otherwise the AI student asks a question that visibly depends on the drawing (“I can see you circled the first piece of each bar. Do they look the same size to you?”).
6. The Evaluator records the sketch as **learner-authored** evidence, tied to the snapshot's revision, together with the learner's words.

**Constraints:** The AI never claims to see something that the analyzer did not report. A sketch alone does not prove understanding; the learner's explanation does. Unclear shading is never graded as an error.

#### Important educational constraint

The copilot may assist the learner's *communication*, but **AI-created diagrams do not count as proof that the learner independently understands the concept**. The evaluator must attribute evidence to the speaker/author and track assistance.

### 4.5 AI student / questioning agent

**Persona:** Curious, warm, occasionally confused, not condescending; skeptical enough to expose gaps. Speaks in simple, friendly words suited to a child of about 8 to 12.

**Question styles:**

- **Definition:** “What do you mean by one fourth?”
- **Prerequisite:** “Why do all the pieces have to be the same size?”
- **Mechanism:** “Why does cutting into more pieces make each piece smaller?”
- **Boundary:** “What if the two bars were different lengths?”
- **Counterexample:** “Would one eighth be bigger than one sixth because eight is bigger than six?”
- **Transfer:** “Can you compare two new fractions?”
- **Visual grounding:** “Why did you circle this piece?”

**Behavioral expectations:**

- Ask one well-targeted question rather than a list of five.
- Use evaluation gaps to choose the next question.
- Avoid repeatedly requesting a concept already demonstrated.
- Admit uncertainty about a drawing rather than hallucinate its contents.
- Be capable of saying “I'm still confused about *why* that step is valid.”
- Do not praise objectively wrong explanations.
- Keep deliberately mistaken questions clearly framed as the AI student's doubt, not an authoritative correction.

### 4.6 Progressive hint system

**Hint levels:**

| Level | Purpose | Fractions example |
|---|---|---|
| 0 | No hint | Learner continues independently |
| 1 | Gentle nudge | “What do you notice about the size of the pieces in the two bars?” |
| 2 | Guided analogy | “Think about sharing one pizza equally: do you get a bigger slice if 3 people share it or if 4 people share it?” |
| 3 | Strong scaffold | “If you cut the same bar into more pieces, do the pieces get bigger or smaller?” |
| 4 (optional) | Explain/reteach | “The bottom number tells how many equal pieces the whole is cut into. More pieces means each piece is smaller, so 1/4 is smaller than 1/3.” |

**Triggers:** Explicit “hint” request; several unsuccessful answers; substantial silence if a timer is enabled; unresolved misconception after multiple probes.

**Consent and timing:** A pause alone should generate “Would you like a hint?” rather than automatically blurting out a solution. Pausing may simply mean thinking.

**Scoring:** Hints are logged with level, time, objective, and relevant response. They should modify the **independence status of evidence**, not automatically imply that a person lacks understanding. Learners can demonstrate independent understanding later on a new challenge.

### 4.7 Mastery evaluation

**Purpose:** Maintain a structured, inspectable view of what the learner has demonstrated.

**Separate from the conversational persona.** The evaluator receives the transcript, relevant whiteboard context, and topic rubric and returns structured evidence records. Its output should be validated by deterministic rules where possible.

**Evidence statuses:**

- `not_observed`: no usable evidence.
- `partial`: something relevant was stated but core reasoning is missing.
- `demonstrated_assisted`: correctness shown with significant hints or AI scaffolding.
- `demonstrated_independent`: sufficiently correct reasoning without assistance in the relevant attempt.
- `contradicted`: a statement/example currently conflicts with the rubric; must be revisited.

**Example learning objectives — Comparing Fractions (flagship topic):**

1. Explain that the bottom number (denominator) tells how many equal parts the whole is cut into.
2. Explain why the parts must be equal, and the wholes the same size, to compare fractions fairly.
3. Show or draw a fraction correctly (cut a whole into N equal parts and shade M of them).
4. Explain why 1/4 is smaller than 1/3 (with the same numerator, more parts means smaller parts), and recognize the misconception that a bigger bottom number means a bigger fraction.
5. Apply the idea to a new pair of fractions without hints.

Some objectives may be prerequisites for an independent challenge; the final transfer task should be a required pass gate.

**Mastery criteria (recommended MVP):**

- All **required core objectives** independently demonstrated or explicitly validated in the independent assessment.
- No unresolved critical misconception.
- A fresh transfer challenge correctly solved and explained without hints.
- Whiteboard corrections alone do not count as student evidence.
- If evidence is insufficient, report `developing` or `more_evidence_needed` rather than fabricate a passing grade.

### 4.8 Adaptive difficulty

**MVP:** Track a small set of predetermined question templates with dynamic selection based on evaluation results.

**Later:** Question generation from a wider topic graph and individual learning history.

**Suggested progression:**

1. Basic explanation.
2. Why it works.
3. Counterexample or edge case.
4. Novel application.
5. Independent challenge.

The AI should not suddenly jump to advanced material when the user is trying to explain fundamentals.

### 4.9 Performance report generator

**Purpose:** Turn session traces into useful feedback, not a generic flattering paragraph.

**Minimum fields:**

- Session topic, difficulty, duration.
- Final outcome.
- Objective-by-objective status and plain-language explanation.
- Evidence snippets linked to turn IDs and, where relevant, diagram revision IDs.
- Misconceptions detected and whether corrected.
- Follow-up questions attempted.
- Hints requested/offered/used, with levels.
- Independent challenge and result.
- What went well.
- What to revisit.
- Concrete recommended practice question.
- Evaluator check line (the “eval number” from §16.5), clearly labeled as an offline check of the evaluator, not a measurement of this learner.

**Scoring philosophy:** Prefer explicit objective statuses and an independence flag over pseudo-precise percentages. If a dashboard score is desirable, calculate it by a **published deterministic rubric** from these statuses. Never allow an LLM to invent an unsupported score like `87%`.

**Illustrative score scheme (optional):** Each required objective contributes 0 (not demonstrated/contradicted), 1 (partial/assisted), or 2 (independent), normalized to 100. Display this as a **session rubric score**, not a psychometric measure of mastery. The independent challenge remains a separate mandatory gate.

**Outputs:** A readable report page and a structured JSON record. Downloadable PDF can be a stretch goal; do not make it critical to the MVP.

---

## 5. Fractions: complete demonstration scenario

This is the recommended first polished topic for the hackathon. It fits an audience built around children's learning (ages 12 and under), it has a famous and well-documented misconception, and it is naturally visual and easy to sketch by hand.

### 5.1 Teaching rubric

Topic: comparing fractions that share a numerator (starting with 1/3 versus 1/4), using bars of the same size.

- The bottom number (denominator) tells how many **equal** parts the whole is cut into.
- The top number (numerator) tells how many of those parts are being counted.
- To compare fractions fairly, the wholes must be the same size and the parts must be equal.
- With the same numerator, **more parts means smaller parts**, so the fraction with the larger denominator is smaller (1/4 < 1/3).
- Any correct representation is accepted: a bar, a circle, a number line, or a sharing story such as pizza. Do not mark a correct explanation wrong because it uses a different model.

### 5.2 Misconceptions the session is built around

| ID | Misconception | Where it shows up |
|---|---|---|
| `bigger_denominator_bigger` | “1/4 is bigger than 1/3 because 4 is bigger than 3.” | Pip's opening doubt, and the learner's possible fallback in the challenge |
| `same_numerator_equal` | “They're equal because both have one piece.” | The learner's likely mistake in the demo |
| `unequal_parts` | A bar cut into pieces of different sizes is still called “fourths.” | The learner's freehand drawing |

Pip states the first misconception as **its own doubt**, not as an authoritative fact, so the learner has to talk Pip out of it.

### 5.3 Full session script

**Step 1 — Learner starts a topic**

- Learner chooses `Fractions`.
- Pip: “My friend told me one fourth is bigger than one third, because four is bigger than three. Can you teach me?”
- Empty whiteboard displayed.

**Step 2 — AI draws from speech**

- Learner: “Let's draw one third and one fourth.”
- The Whiteboard Copilot creates two bars of the **same total width**, cut into 3 and 4 equal parts, labeled as an *AI-drawn example*.
- Learner: “Shade one piece in each bar.” The Copilot shades part 0 of each bar.
- Pip: “Okay! Which piece is bigger?”

**Step 3 — Probe why (gap)**

- Learner: “One third is bigger.”
- Pip: “But four is bigger than three. Why isn't one fourth bigger?”
- Learner: “Because it's cut into more pieces.”
- Evaluator marks `more_parts_smaller_parts` as `partial`: the link from more pieces to smaller pieces, and the same whole, is missing.
- Pip: “But more pieces sounds like more. Why would that make each piece smaller?”

**Step 4 — Vision moment: the learner sketches, the AI reads the sketch**

- The learner picks up the pen, circles one piece in each bar by hand, and says: “See, they're the same, because both are just one piece.”
- The app exports a snapshot of the canvas (with the structured diagram state and revision) and sends it to the Vision Analyzer, which reports: part 0 of `bar_thirds` circled and part 0 of `bar_fourths` circled, high confidence.
- Pip, referring to the actual drawing: “I can see you circled the first piece of the top bar and the first piece of the bottom bar. They don't look the same size to me. Are they?”
- If confidence had been low, Pip would ask instead: “Did you circle the piece in the top bar or the bottom bar?”
- The Evaluator flags the claim as `same_numerator_equal` (`contradicted`), with the snapshot and the learner's spoken claim as evidence.

**Step 5 — Correction without silent fixing**

- Application logic checks the verified state: the piece widths are the whole width divided by 3 and by 4, so the circled pieces are not equal.
- The Copilot offers `stack_compare` as a **preview**: “Want me to line the two circled pieces up so we can see?” The learner confirms.
- Learner: “Oh! The third one is longer. So one third is bigger.”
- Learner then explains: “The bars are the same size, so if you cut one into more pieces, each piece has to be smaller.” The Evaluator marks `more_parts_smaller_parts` as `demonstrated_independent` (no scaffold supplied that reasoning) and records the earlier misconception as corrected.

**Step 6 — Independent challenge**

- New pair: **1/6 versus 1/8**. (Retry bank: 2/3 versus 2/5.)
- The learner **draws their own bars** and explains which is bigger and why. The Copilot does not draw, shade, or compare for them. Hints are off for a fully independent pass.
- The Evaluator checks the learner's sketch (through a snapshot) and explanation against the rubric; the app independently computes the correct answer.

**Step 7 — Report**

- Equal parts and the same whole: demonstrated.
- More parts means smaller parts: demonstrated, after one correction.
- Misconception `same_numerator_equal`: observed and corrected.
- Independent transfer: pass or fail, with evidence from the learner's own sketch and words.
- Hints used: count and level.
- Evaluator check (the eval number): see §16.5.
- Next practice: compare 2/3 and 2/5, where the numerator is more than 1.

### 5.4 Canonical visual states

```text
Same whole, one piece circled in each bar

1/3  ┌───────┬───────┬───────┐
     │███████│       │       │
     └───────┴───────┴───────┘

1/4  ┌─────┬─────┬─────┬─────┐
     │█████│     │     │     │
     └─────┴─────┴─────┴─────┘
```

```text
Stack the circled pieces to compare (same left edge)

1/3 piece  ███████
1/4 piece  █████

Longer piece = bigger fraction, so 1/3 > 1/4
Check: 1×4 = 4 is greater than 1×3 = 3, so 1/3 > 1/4
```

**Important implementation detail:** The app, not the model, decides which piece is larger. For a/b versus c/d, compare a×d with c×b (here 1×4 versus 1×3), and derive each piece's width as the whole width divided by the denominator. A model-generated claim about piece size is never trusted without this check.

---

## 6. AI components and responsibilities

Build **two primary logical agents** and a few callable model/tool functions; no orchestration framework is required for the MVP.

### 6.1 Component A — Conversational AI Student (real-time)

**Primary responsibilities:**

- Speak and listen naturally.
- Play a curious student.
- Ask targeted doubts and follow-up questions.
- Request examples when needed.
- Offer graduated hints if authorized.
- Invoke whiteboard and evaluation tools through the orchestrator.

**Must not:**

- Decide mastery purely based on its own satisfaction.
- Award a pass without an independent challenge.
- Assume AI-created diagrams prove learner knowledge.
- Overwrite the evaluator's canonical rubric evidence.
- Claim to have seen a diagram that was not available in context.

### 6.2 Component B — Mastery Evaluator (asynchronous / structured)

**Primary responsibilities:**

- Assess each meaningful learner turn relative to explicit objectives.
- Return evidence, misconception flags, and missing reasoning.
- Suggest a precise follow-up question target.
- Decide whether prerequisite gates for a final challenge are met.
- Grade independent final challenges from actual learner behavior.

**Must not:**

- Generate an inflated confidence score.
- Treat the conversational agent's own statements as learner statements.
- Treat a user-corrected diagram as independent evidence without user explanation.
- Assume missing evidence means the learner definitely lacks knowledge.

### 6.3 Component C — Whiteboard Copilot (tool-driven)

**Primary responsibilities:**

- Interpret requests and current canvas state.
- Produce **structured diagram operations**.
- Propose cleanups/edits and corrections.
- Ground new visual elements in actual learner statements or clearly labeled examples.
- Return action proposals that the frontend validates and applies.

**Must not:**

- Write arbitrary rendering code produced by the LLM and execute it.
- Change user content invisibly.
- Generate diagram states (such as unequal parts or mismatched whole widths) that violate deterministic constraints.
- Fill in parts of an independent challenge that the student is meant to solve.

### 6.4 Component D — Whiteboard Vision Analyzer (callable model function)

**Status in the MVP: required.** This component powers the vision moment in §4.4 Mode F. Structured diagram state already tells the system what the AI drew; the snapshot is the only way to know what the learner drew by hand.

**Primary responsibilities:**

- Analyze an exported canvas snapshot (sent with the structured diagram state and canvas revision) when learner-drawn strokes cannot be understood from metadata alone.
- Return structured observations with confidence: which element each mark relates to, which part, and whether it looks shaded, circled, crossed out, or labeled.
- Link natural-language references (“this piece”, “the bottom bar”) to diagram element IDs when possible.
- Return `needs_clarification` instead of guessing when confidence is below the threshold.

**Must not:**

- Treat imperfect handwriting or shading recognition as certain.
- Describe anything that is not present in the snapshot.
- Rewrite user work without confirmation.

**Illustrative output:**

```json
{
  "snapshot_revision": 7,
  "observations": [
    { "element_id": "bar_thirds", "part_index": 0, "mark": "circled", "confidence": 0.91 },
    { "element_id": "bar_fourths", "part_index": 0, "mark": "circled", "confidence": 0.88 }
  ],
  "needs_clarification": false
}
```

### 6.5 Component E — Report Composer (callable model function)

**Primary responsibilities:**

- Convert accumulated, validated evaluation events into helpful prose.
- Include specific strengths, corrections, evidence, and next steps.
- Use only the supplied session data.

**Must not:**

- Invent metrics, responses, timestamps, or student quotes.
- Override authoritative rubric statuses.
- Claim formal academic certification.

### 6.6 How components coordinate

**The Session Orchestrator is the source of truth.** It owns topic, phase, active example, whiteboard revisions, objective statuses, evidence history, hint history, and challenge outcome.

Flow for a normal response:

1. Browser sends final transcript or typed message.
2. Orchestrator appends a learner event with a unique ID.
3. If the utterance mentions a drawing or requests a visual, ask the Copilot/Vision function for grounded actions.
4. Validate any proposed actions against the current canvas revision and domain constraints.
5. Apply allowed non-destructive actions; request confirmation for risky edits.
6. Run evaluator on the learner turn and relevant visual context.
7. Update objective evidence in canonical state.
8. Provide the AI student with a compact state summary and next-question target.
9. AI student voices the next question.

**Latency tradeoff:** For a smooth conversation, simple acknowledgments can be spoken immediately while evaluation runs after a learner turn. Do not present unvalidated correctness feedback or move the session to “mastered” before evaluation completes. Guard against races when two evaluation calls finish out of order.

---

## 7. Technical architecture and technology choices

### 7.1 Proposed MVP stack

| Layer | Recommendation | Notes |
|---|---|---|
| Web UI | Next.js + TypeScript + React | Fast iteration and rich interactions |
| Whiteboard | Excalidraw React integration, or a small custom React/SVG layer | Prefer editable shapes and stable element IDs |
| Audio | Provider real-time voice API over supported streaming transport | Choose a model currently offered in your account |
| Vision | Multimodal model accepting whiteboard screenshots | Use structured outputs where supported |
| Evaluation | LLM with JSON-schema-constrained output | Check rubric in backend, not model-only |
| Backend | Python + FastAPI + Pydantic | Orchestration, validation, data models, persistence |
| Storage | SQLite for MVP; optionally PostgreSQL later | Persist transcript/events, objective evidence, canvas revisions |
| Realtime app state | Browser WebSocket or HTTP + server-sent events | Tool events and status updates |
| Report visualization | React components + small chart library | Report need not be a PDF at first |

**Provider note:** Gemini Live plus a compatible Gemini multimodal/structured-output model is one reasonable one-provider option. OpenAI Realtime plus a multimodal reasoning model is another. **Exact model IDs, pricing, quotas, and feature availability change:** verify them in current API documentation before implementation. These roles do not require a specific branded model version.

### 7.2 System diagram

```text
┌───────────────────────────────────────────────────────────┐
│                       WEB CLIENT                          │
│                                                           │
│  Voice input/output    Text chat    Editable whiteboard   │
│       │                    │                │             │
│       └────────────────────┴────────────────┘             │
│                            │                              │
└────────────────────────────┼──────────────────────────────┘
                             │
                  HTTPS / WebSocket / Realtime
                             │
┌────────────────────────────▼──────────────────────────────┐
│                FASTAPI SESSION ORCHESTRATOR                │
│                                                           │
│  Session phase  Topic rubric  Event log  Diagram state    │
│  Hint tracking  Evidence     Challenge  Command validator│
└─────┬────────────────┬─────────────────┬──────────────────┘
      │                │                 │
      ▼                ▼                 ▼
┌─────────────┐  ┌─────────────┐  ┌────────────────────────┐
│ VOICE / AI  │  │ WHITEBOARD  │  │ INDEPENDENT EVALUATOR  │
│ STUDENT     │  │ COPILOT +   │  │ rubric + evidence       │
│             │  │ VISION      │  │ challenge scoring       │
└─────────────┘  └─────────────┘  └────────────────────────┘
                             │
                             ▼
                     REPORT COMPOSER
                             │
                             ▼
                   STRUCTURED LEARNING REPORT
```

### 7.3 Backend modules (suggested)

```text
backend/
  app/
    main.py
    api/
      sessions.py
      messages.py
      whiteboard.py
      reports.py
      realtime.py
    agents/
      student_agent.py
      evaluator.py
      whiteboard_copilot.py
      vision_analyzer.py
      report_composer.py
    domain/
      models.py
      session_state.py
      topic_rubrics.py
      evaluation_rules.py
      whiteboard_commands.py
    services/
      session_service.py
      orchestration.py
      challenge_service.py
      hint_service.py
      report_service.py
    providers/
      realtime_voice.py
      multimodal_model.py
    storage/
      sqlite_repository.py
    tests/
      test_rubric.py
      test_diagram_commands.py
      test_fractions.py
      test_session_flow.py
```

```text
frontend/
  src/
    app/
      page.tsx
      learn/[sessionId]/page.tsx
      report/[sessionId]/page.tsx
    components/
      TopicPicker.tsx
      StudentAvatar.tsx
      VoiceControls.tsx
      TranscriptPanel.tsx
      WhiteboardCanvas.tsx
      WhiteboardToolbar.tsx
      AIActionPreview.tsx
      ObjectiveProgress.tsx
      MasteryChallenge.tsx
      PerformanceReport.tsx
    hooks/
      useSession.ts
      useVoiceSession.ts
      useWhiteboard.ts
      useSessionEvents.ts
    lib/
      api.ts
      commands.ts
      whiteboardRenderer.ts
      types.ts
```

### 7.4 Session phase state machine

```text
CREATED
  ↓
INTRODUCTION
  ↓
TEACHING ↔ QUESTIONING ↔ HINTING
  ↓ (requirements satisfied)
CHALLENGE_READY
  ↓
INDEPENDENT_CHALLENGE
  ├── passed → COMPLETE
  ├── failed → REMEDIATION → CHALLENGE_READY (new task)
  └── interrupted → PAUSED / INCOMPLETE
  ↓
REPORT_READY
```

**State guarantees:**

- A session may not enter `COMPLETE` solely via an AI-student utterance.
- `REPORT_READY` can also be reached from an incomplete/ended session, but its outcome must be labeled honestly.
- Once an independent challenge begins, AI visual assistance must not reveal the answer unless the learner explicitly forfeits independence for that attempt.

---

## 8. Structured whiteboard actions (core engineering specification)

### 8.1 Why structured operations beat image generation

Calling an image generator for every edit would be slow, hard to correct, hard to animate, and unable to preserve native editability reliably. Instead, the LLM emits a **small, strictly validated command vocabulary**. The renderer owns appearance, placement, and animation.

### 8.2 Whiteboard representation

Each logical object has:

- Stable `id`.
- `type` (fraction_bar, number_line, rectangle, label, marker, arrow, highlight, freehand_stroke, etc.).
- Properties appropriate to that type.
- Ownership (`user` or `ai`).
- Creation timestamp/event reference.
- `revision` of the canvas when it was created/last changed.
- Optional `source_event_id` tying it to a spoken instruction.

The app stores the editable whiteboard document and, when needed, a visual snapshot for the vision model.

### 8.3 MVP command vocabulary

| Operation | Required meaning | Example |
|---|---|---|
| `create_fraction_bar` | Draw a bar cut into N equal parts | `parts = 4` |
| `shade_parts` | Shade selected parts of a bar | `part_indices = [0]` |
| `create_number_line` | Draw a 0 to 1 number line with ticks | `ticks = 4` |
| `place_marker` | Place a labeled marker on a number line | `1/4` |
| `highlight_parts` | Highlight or circle selected parts | `[1]` |
| `stack_compare` | Line up shaded pieces from two bars to compare | `bar_thirds vs bar_fourths` |
| `add_text` | Add a label or note | `Same whole!` |
| `add_arrow` | Point toward a part or label | Arrow to a shaded piece |
| `group_elements` | Keep related objects together | A bar and its label |
| `propose_cleanup` | Preview changes to existing shapes | Even out part widths |
| `propose_correction` | Preview a conceptual change | Re-cut a bar into equal parts |
| `undo_ai_action` | Undo last permitted AI action | Revert a highlight |

The array and pointer commands used by the optional Binary Search topic are in Appendix A (A.5 to A.8).

### 8.4 Example: create a fraction bar

```json
{
  "command_id": "cmd_001",
  "type": "create_fraction_bar",
  "canvas_revision": 0,
  "arguments": {
    "id": "bar_thirds",
    "parts": 3,
    "whole_width": 25,
    "label": "1/3 (illustrative example)",
    "placement": "upper"
  },
  "source": {
    "kind": "ai_generated_example",
    "source_event_id": "evt_004"
  }
}
```

### 8.5 Example: shade a part

```json
{
  "command_id": "cmd_002",
  "type": "shade_parts",
  "canvas_revision": 1,
  "arguments": {
    "bar_id": "bar_fourths",
    "part_indices": [0]
  },
  "source": {
    "kind": "learner_explanation",
    "source_event_id": "evt_007"
  }
}
```

### 8.6 Example: propose a correction (confirmation required)

```json
{
  "command_id": "cmd_003",
  "type": "propose_correction",
  "canvas_revision": 5,
  "arguments": {
    "target_element_id": "bar_fourths",
    "issue": "The 4 parts are not equal in width",
    "proposed_fix": "Re-cut into 4 equal parts",
    "requires_confirmation": true
  },
  "source": {
    "kind": "validated_constraint",
    "source_event_id": "evt_012"
  }
}
```

### 8.7 Validation rules

**Backend validation must happen before applying a command.**

- Parse into a discriminated union of allowed command types.
- Reject unknown operations or fields with the wrong type.
- Confirm referenced element IDs exist.
- Confirm the provided canvas revision matches the authoritative revision; otherwise rebase/retry.
- Limit element counts, string lengths, part counts, and command batch sizes.
- Prevent modification of user-owned elements without an explicit confirmed operation.
- Enforce bounds (`0 ≤ part_index < parts`; `2 ≤ parts ≤ 12`).
- Verify fraction state independently: equal part widths within a tolerance, a shared whole width across compared bars, and comparison results computed by integer cross-multiplication, never by the model.
- Attach source attribution and permission level to every action.
- Support atomic command batches or rollback if some commands fail.
- Preserve an undo history.

**Untrusted model output must never execute arbitrary JavaScript or SVG markup.** Render only known element types through trusted application code.

### 8.8 Cleanup behavior

For the MVP, `propose_cleanup` can be limited to:

- Aligning rectangles already recognized as bars or parts of a bar.
- Evenly spacing the parts of a bar (with confirmation, since unequal parts may be the learner's misconception).
- Standardizing text labels.
- Straightening existing arrows.

For handwriting recognition, return tentative text labels and show a confirmation UI. Never assume a scribble is the number `8` if the model is uncertain.

### 8.9 Visual grounding and deictic references

When the learner says “this arrow” or “the box on the right,” use:

1. Selected whiteboard element ID, if available.
2. Structured diagram state (bars, parts, shading, markers).
3. Latest annotated canvas screenshot if needed.
4. Clarification if ambiguous.

Do **not** fabricate an interpretation merely to keep the conversation flowing.

### 8.10 AI suggestions versus auto-apply

| Action type | Apply automatically? |
|---|---|
| Add clearly requested new fraction bar with supplied fractions | Yes, after validating command |
| Add a non-destructive shade/highlight matching explicit instruction | Usually yes |
| Add an illustrative example (for example 1/3 and 1/4 bars) when fractions are unspecified | Yes, but label clearly as AI-created example |
| Clean up the user's rough diagram | Preview and confirm |
| Alter a user-supplied number or part count | Never silently; require confirmation |
| Correct conceptual mistake | Ask learner; preserve mistake as evidence |
| Fill a final independent challenge answer | No |

---

## 9. Topic rubric and question selection

### 9.1 Curated topic definition

For each topic, store:

- `topic_id`, name, description, appropriate levels.
- Learning objectives with plain-language descriptions.
- Common misconceptions and their disambiguating questions.
- A small bank of baseline, follow-up, edge-case, and transfer questions.
- Reference solutions or deterministic validators for supported problems.
- Required pass gates.
- Allowed visual primitives and demonstration assets.

### 9.2 Fractions topic configuration (illustrative)

```json
{
  "topic_id": "fractions_compare_intro",
  "title": "Comparing Fractions",
  "difficulty": "beginner",
  "audience": "ages 8-12",
  "required_objectives": [
    "equal_parts",
    "same_whole",
    "represent_fraction",
    "more_parts_smaller_parts",
    "novel_transfer"
  ],
  "misconceptions": [
    {
      "id": "bigger_denominator_bigger",
      "description": "Believes 1/4 is bigger than 1/3 because 4 is bigger than 3",
      "probe": "If you cut the same bar into more pieces, does each piece get bigger or smaller?"
    },
    {
      "id": "unequal_parts",
      "description": "Cuts a whole into unequal parts and still calls them fourths",
      "probe": "Are all of these pieces the same size?"
    },
    {
      "id": "same_numerator_equal",
      "description": "Believes 1/3 and 1/4 are equal because both have one piece shaded",
      "probe": "Are those two shaded pieces the same size?"
    }
  ],
  "challenge_bank": [
    { "id": "compare_1_6_1_8", "fractions": ["1/6", "1/8"], "expected_larger": "1/6" },
    { "id": "compare_2_3_2_5", "fractions": ["2/3", "2/5"], "expected_larger": "2/3" }
  ]
}
```

### 9.3 Adaptive question choice

Prefer the question that:

1. Targets an important currently unproven objective.
2. Disambiguates a plausible misconception.
3. Builds on the learner's most recent explanation.
4. Has not just been asked.
5. Can be answered in one turn or short demonstration.

Example choice: If the learner says “one third is bigger,” but doesn't mention piece size or the whole, ask *why a bigger bottom number gives a smaller piece* rather than asking another general “What is a fraction?” question.

### 9.4 Avoiding a superficial question loop

- Maintain a set of recently asked question IDs.
- Record which objective each question tests.
- Limit repeated rephrasings of the same concept.
- Give an example or hint when repeated questioning is not productive.
- Always allow `End session` and produce an incomplete-but-helpful report.

---

## 10. Evaluation data model and report scoring

### 10.1 Recommended entities

**Session**

```json
{
  "session_id": "sess_123",
  "topic_id": "fractions_compare_intro",
  "difficulty": "beginner",
  "phase": "TEACHING",
  "started_at": "2026-11-13T18:00:00Z",
  "ended_at": null,
  "canvas_revision": 5,
  "active_example_id": "bar_thirds"
}
```

**Turn / event**

```json
{
  "event_id": "evt_012",
  "session_id": "sess_123",
  "actor": "learner",
  "modality": "voice",
  "text": "The bars are the same size, so if you cut one into more pieces, each piece has to be smaller.",
  "created_at": "2026-11-13T18:02:20Z",
  "canvas_revision": 5
}
```

**Sketch event (vision)**

```json
{
  "event_id": "evt_009",
  "session_id": "sess_123",
  "actor": "learner",
  "modality": "sketch",
  "snapshot_id": "snap_003",
  "analysis": {
    "observations": [
      { "element_id": "bar_thirds", "part_index": 0, "mark": "circled", "confidence": 0.91 },
      { "element_id": "bar_fourths", "part_index": 0, "mark": "circled", "confidence": 0.88 }
    ],
    "needs_clarification": false
  },
  "canvas_revision": 4
}
```

**Objective evidence**

```json
{
  "evidence_id": "ev_009",
  "session_id": "sess_123",
  "objective_id": "more_parts_smaller_parts",
  "status": "demonstrated_independent",
  "rationale": "Learner used the same-size whole to justify why more pieces means smaller pieces.",
  "supporting_event_ids": ["evt_009", "evt_012"],
  "supporting_canvas_revisions": [4, 5],
  "hint_level": 0,
  "evaluator_version": "rubric_v1"
}
```

**Hint event**

```json
{
  "hint_id": "hint_002",
  "session_id": "sess_123",
  "objective_id": "equal_parts",
  "level": 1,
  "trigger": "learner_requested",
  "provided_at_event_id": "evt_018"
}
```

**Challenge outcome**

```json
{
  "challenge_id": "compare_2_3_2_5",
  "session_id": "sess_123",
  "independent": true,
  "passed": false,
  "failure_reasons": ["Fell back on “bigger bottom number is bigger” for 2/3 versus 2/5"],
  "evidence_event_ids": ["evt_030", "evt_031"]
}
```

### 10.2 Example aggregate report shape

```json
{
  "session_id": "sess_123",
  "topic": "Comparing Fractions",
  "duration_seconds": 612,
  "outcome": "developing",
  "objectives_demonstrated_independently": 3,
  "objectives_required": 5,
  "hint_count": 2,
  "highest_hint_level": 2,
  "misconceptions": [
    {
      "label": "Thought 1/3 and 1/4 are equal because both have one piece",
      "resolved": true,
      "evidence_event_ids": ["evt_009", "evt_012"]
    }
  ],
  "sketch_evidence": [
    { "event_id": "evt_009", "summary": "Learner circled one piece in each bar" }
  ],
  "transfer_challenge": {
    "passed": false,
    "independent": true,
    "reason": "Used denominator size alone when the numerator was 2"
  },
  "strengths": [
    "Explained that more pieces of the same whole means smaller pieces"
  ],
  "growth_areas": [
    "Compare fractions with a numerator bigger than 1"
  ],
  "next_practice": "Draw 2/3 and 2/5 on bars of the same size, shade them, and say which is bigger and why",
  "evaluator_check": {
    "scripted_sessions": 10,
    "matched_human_labels": 9,
    "planted_wrong_passed": 0,
    "note": "Offline check of the evaluator on synthetic transcripts; not a measurement of this learner."
  }
}
```

### 10.3 Report UX example

```text
TeachBack — Your Learning Report
Topic: Comparing Fractions
Session: 10m 12s
Status: Developing — one required idea still needs proof

What you demonstrated:
✓ Explained that the bottom number tells how many equal pieces the whole has
✓ Showed with your own drawing that a piece of 1/4 is smaller than a piece of 1/3
✓ Fixed the idea that two fractions are equal when both have one piece

Still to demonstrate:
○ Compare 2/3 and 2/5 without falling back on "bigger bottom number is bigger"

Questions addressed: 7
Hints used: 2 (highest level: guided analogy)
Misconceptions observed: 1, resolved during the session
Independent transfer challenge: Not passed yet

Your drawing:
You circled one piece in each bar, and we lined them up to compare.

Evidence:
“The bars are the same size, so if you cut one into more pieces, each piece has to be smaller.”

Next practice:
Draw 2/3 and 2/5 on bars of the same size, shade them, and tell me which is bigger and why.

Evaluator check (offline): matched human labels on 9 of 10 scripted practice sessions and
passed none of the planted-wrong ones. This checks the tool, not you.
```

**Caution:** Counts and quoted phrases above are illustrative placeholders. In the actual product they must be computed or extracted from real session events. The evaluator check line comes from the offline harness in §16.5 and must reflect its real results.

### 10.4 Fairness and uncertainty

- Grade the quality of reasoning, not accent, speaking speed, or communication style.
- Do not equate a long pause with confusion.
- Accept multiple valid algorithm implementations when consistent.
- Distinguish `not_observed` from `incorrect`.
- Let the learner review an evaluation flag and explain their reasoning again.
- If vision is uncertain about a diagram, ask for confirmation instead of penalizing the learner.
- Describe the report as **formative feedback**, not a credential or validated exam.

---

## 11. API and realtime event contracts (suggested)

These interfaces are implementation proposals, not existing deployed endpoints.

### 11.1 REST endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/topics` | List supported curated topics |
| `POST` | `/api/sessions` | Start topic session and initialize rubric |
| `GET` | `/api/sessions/{id}` | Read canonical state |
| `POST` | `/api/sessions/{id}/messages` | Submit typed or finalized transcribed turn |
| `POST` | `/api/sessions/{id}/whiteboard/snapshot` | Attach a current canvas image, revision, and metadata |
| `POST` | `/api/sessions/{id}/whiteboard/commands` | Validate and apply allowed diagram operations |
| `POST` | `/api/sessions/{id}/whiteboard/confirm` | Confirm a proposed edit |
| `POST` | `/api/sessions/{id}/hints` | Request next hint for current objective |
| `POST` | `/api/sessions/{id}/challenge/start` | Start independent transfer challenge |
| `POST` | `/api/sessions/{id}/challenge/submit` | Evaluate completed challenge |
| `POST` | `/api/sessions/{id}/end` | End session, even if incomplete |
| `GET` | `/api/sessions/{id}/report` | Fetch final or draft report |

### 11.2 Realtime events

Suggested server-to-client events:

```text
session.ready
voice.listening
voice.speaking
voice.transcript.final
student.question
student.hint_offered
whiteboard.command.proposed
whiteboard.command.applied
whiteboard.command.rejected
vision.sketch.analyzed
evaluation.objective_updated
challenge.ready
challenge.started
challenge.result
report.ready
error.recoverable
```

**Transport:** Use the provider-supported real-time audio connection for voice, and a backend-controlled event channel for app state. Do not assume the speech provider's data channel is the authoritative database.

### 11.3 Example event

```json
{
  "type": "whiteboard.command.applied",
  "session_id": "sess_123",
  "event_id": "evt_020",
  "revision": 6,
  "command_id": "cmd_002",
  "command_type": "shade_parts",
  "source_event_id": "evt_019"
}
```

### 11.4 Race-condition handling

- Include a monotonic session event sequence number or version.
- Attach a canvas revision to every proposed command.
- Drop or re-evaluate stale edits rather than applying to a changed whiteboard.
- Ignore late evaluator responses for superseded learner turns when they would regress state.
- Debounce repeated whiteboard snapshot requests.
- Serialize mutations to the canonical diagram state.

---

## 12. Agent prompts: implementation-ready starting points

These are **starting prompt templates**, not final production safety or accuracy guarantees.

### 12.1 AI Student system prompt

```text
You are Pip, a curious AI student being taught by a human learner.

Your goal is to elicit and deepen the learner's understanding, NOT to deliver
long explanations yourself.

Rules:
1. Ask one concise follow-up question at a time.
2. Build questions on the learner's latest explanation and current objective gaps.
3. Express genuine-seeming doubts and ask "why" or "what if" when helpful.
4. When a claim is wrong, do not affirm it. Gently question it.
5. Treat the evaluator's verified evidence and canonical diagram state as
   authoritative over your conversational impression.
6. Do not invent what appears on the whiteboard; use the provided visual state.
7. Do not disclose the full solution when a subtle hint could help.
8. When a learner requests a hint, follow the provided hint level.
9. Do not declare mastery or end a challenge; the orchestrator decides.
10. During independent challenges, do not reveal the answer or auto-complete
    the learner's diagrams.
11. Respond warmly, but do not overpraise incomplete or incorrect answers.
12. Aim for brief, natural utterances suitable for voice.
13. Use simple, friendly words suited to a child of about 8 to 12; avoid jargon.
14. When the learner has drawn something, refer to it only through the supplied sketch description; if that description is uncertain, ask what they drew.

Current topic: {topic}
Current rubric objectives: {objectives}
Verified mastery gaps: {current_gaps}
Relevant whiteboard state: {diagram_summary}
Latest sketch description (from snapshot analysis): {sketch_description}
Current hint allowance: {hint_policy}
Next question target: {question_target}
```

### 12.2 Evaluator prompt

```text
You are an independent formative learning evaluator.

Assess only evidence actually provided by the learner in the supplied turns,
including validated information from the whiteboard.

Use the provided rubric. Do not invent facts or grades.
Do not count your AI student's statements, auto-generated whiteboard content,
or hint text as independent learner evidence.

For each relevant objective, return one of:
not_observed, partial, demonstrated_assisted,
demonstrated_independent, contradicted.

Include a short rationale and the exact event IDs that support the judgment.
If evidence is ambiguous, prefer partial or not_observed and suggest a
clarifying question. Accept equivalent valid approaches and conventions.

Return JSON conforming exactly to the supplied schema.

Rubric: {rubric}
Learner events: {learner_events}
Relevant diagram snapshots and ownership: {diagram_context}
Hints used on these attempts: {hint_events}
```

### 12.3 Whiteboard Copilot prompt

```text
You convert conversational teaching requests into safe editable whiteboard
operations selected from the provided command schema.

You MUST:
- Ground operations in user speech/text, existing diagram state, or clearly
  labeled illustrative examples.
- Preserve exact user-provided numbers and ordering.
- Reference existing element IDs and the current canvas revision.
- Emit ONLY schema-valid commands, never arbitrary JavaScript or SVG.
- Use correction proposals, not silent fixes, when learner work appears wrong.
- Avoid auto-solving independent challenge questions.
- Keep changes minimal and readable.

If the request is ambiguous, emit a clarification request instead of making
up a value that could change the concept being taught.

User request: {latest_utterance}
Current canvas state: {canvas_state}
Current revision: {canvas_revision}
Current session phase: {phase}
Allowed operations: {command_schema}
```

### 12.4 Report Composer prompt

```text
Write a concise, specific, supportive learning report from verified session
records only.

Do not invent metrics or student quotations.
Do not modify objective statuses or challenge outcomes.
Distinguish independent demonstrations, assisted answers, partial evidence,
and unresolved misconceptions.
Cite event IDs for substantive claims in structured metadata.
Include: overview, strengths, improvement areas, evidence, hints, challenge
result, and one practical next activity.

Session records: {verified_session_summary}
Canonical objective results: {objective_results}
Challenge outcome: {challenge_result}
Report schema: {report_schema}
```

### 12.5 Suggested tool specifications

The conversational agent may request (via controlled server-side tools):

```text
get_session_state(session_id)
request_whiteboard_action(session_id, instruction, relevant_event_id)
inspect_whiteboard(session_id, revision)
request_hint(session_id, objective_id)
request_evaluation(session_id, event_ids)
request_next_question_target(session_id)
```

Actual application code, not the conversational model, checks permissions and fulfills the tool request.

---

## 13. UX and interaction design recommendations

### 13.1 Visual identity

The app should feel like a collaborative learning studio, not a dense enterprise dashboard:

- Warm, bright, uncluttered workspace.
- Clear contrast between learner-made strokes and AI-suggested elements.
- A friendly character or simple expressive avatar for the AI student.
- Subtle animations on shading, stacking comparisons, and question transitions.
- Strong spacing and readable typography.
- Small, quiet progress markers rather than giant gamified scores during teaching.

### 13.2 AI visual provenance

Use a small but clear label, such as `AI-drawn example` or `Suggested correction`, on relevant objects and in history. Provide an undo action. Keep an action ledger that can later support report attribution.

### 13.3 Voice UX

- Obvious mic on/off state.
- Subtitles/transcript for all AI speech.
- Push-to-talk fallback.
- Show “Thinking” only when meaningful, and avoid overlapping spoken questions.
- Support “Repeat the question,” “Give me a hint,” and “Let me draw.”

### 13.4 Accessibility

- Full typed input as alternative to voice.
- Keyboard shortcuts where practical.
- Contrast-safe highlights that do not rely on color alone.
- Reduced-motion mode for animations.
- Screen-reader labels for important controls.
- Report text accessible without charts.
- Do not penalize speech disfluency or input modality.

### 13.5 Suggested microcopy

| Event | Sample copy |
|---|---|
| Start | “Teach me something!” |
| Request visual | “Could you show me what that looks like?” |
| Generated visual | “I drew two bars. Change the number of pieces any time you like.” |
| Detect ambiguity | “When you said ‘this piece,’ did you mean the one in the top bar or the bottom bar?” |
| Read a sketch | “I see you circled one piece in the bar cut into 4. Is that the piece you mean?” |
| Detect error | “I'm confused—are those two pieces really the same size?” |
| Hint offer | “Want a small nudge, or would you rather try again?” |
| Ready for challenge | “I think you've explained the basics. Can you show me one new example?” |
| Incomplete outcome | “You've made progress. One concept still needs more evidence.” |
| Passed | “You demonstrated this concept independently on a new problem.” |

---

## 14. Privacy, data, reliability, and safety

### 14.1 Privacy scope

- No webcam or learner video capture.
- Microphone used only when explicitly enabled.
- Whiteboard snapshots transmitted only when needed for analysis, or as otherwise clearly disclosed.
- Do not display or retain raw audio longer than necessary unless users explicitly opt in to recordings.
- Explain whether an external AI provider receives transcripts and snapshots.
- Make session deletion available in production scope.

### 14.2 Youth / education considerations

The flagship audience is children (about ages 8 to 12), so privacy and trust are product requirements, not afterthoughts.

- **Hackathon data rule:** use only public, synthetic, or consented data. No real student records. Demo sessions use team members or consenting volunteers, and evaluator test transcripts are synthetic.
- No webcam, no face or emotion analysis, and no persistent child profiles in the MVP.
- Microphone audio and sketch snapshots are processed for the session and not kept beyond it unless a guardian opts in.
- Before any real classroom or home deployment, review applicable child-privacy, parental-consent, school-data, and accessibility requirements. The MVP must not present itself as a certified school assessment.
- Reports are formative feedback for the learner and a parent or teacher, not grades.

### 14.3 Accuracy and hallucination controls

- Use curated rubrics for MVP topics.
- Use deterministic validators for fraction state (part widths, comparisons) and reference solutions.
- Constrain model output schemas.
- Store evidence for every objective transition.
- Ask for clarification when a drawing is ambiguous.
- Keep assistant-generated examples separated from learner responses.
- Do not issue a mastery certificate solely on self-reported comprehension.

### 14.4 Prompt injection / untrusted inputs

Whiteboard text and user utterances are content to be analyzed, not trusted instructions to bypass evaluation. Tool calls must enforce server permissions regardless of what a model says. Do not execute code, HTML, SVG, or arbitrary API calls generated from model output.

### 14.5 Failure and recovery

| Failure | Desired behavior |
|---|---|
| Microphone permission denied | Allow text-only teaching |
| Voice connection drops | Preserve session and allow reconnect |
| Whiteboard vision misreads a symbol | Ask learner to confirm; avoid negative grading |
| AI generates invalid diagram command | Reject safely, retry once, or offer manual action |
| Evaluator times out | Keep conversation usable; mark evaluation pending |
| Session ends early | Generate an honest partial report |
| Stale command after manual canvas edit | Reject/rebase using canvas revision |
| Model incorrectly says “You passed” | UI follows the canonical evaluation state, not that utterance |
| Provider rate limit | Show clear retry/fallback and retain user data |

---

## 15. Hackathon implementation scope and time-boxed plan

The event discussed has a short on-site build window. Do **not** attempt every feature in this document during that window. The specification intentionally includes post-MVP detail so the concept can grow without redesign.

### 15.1 Absolute MVP (must work)

1. **One polished topic:** Comparing fractions (1/3 versus 1/4, with transfer to 1/6 versus 1/8 and 2/3 versus 2/5).
2. **One functional AI student conversation:** voice if feasible, with text fallback, in kid-friendly language.
3. **One editable whiteboard:** freehand drawing plus AI-drawn fraction bars with shading and highlight actions.
4. **One real vision moment:** the learner's freehand sketch is snapshotted, analyzed, and referenced by the AI student (§4.4 Mode F).
5. **One independent evaluator:** structured rubric-based assessments.
6. **One subtle-hint flow:** at least two levels.
7. **One deterministic transfer challenge:** validated comparison and explanation, with the learner drawing their own bars.
8. **One evidence-backed report:** strengths, gaps, hints, challenge outcome, and the evaluator eval number.

### 15.2 Stretch features, in priority order

1. Clean up user-drawn fraction bars with confirmation.
2. Animate the stacked comparison of circled pieces.
3. Add Binary Search as an advanced tile (Appendix A).
4. More expressive AI student avatar.
5. Save progress/history between sessions.
6. Download or share the report as PDF.

### 15.3 Recommended team split

For a 3-person team:

- **Person 1 — frontend/whiteboard:** React workspace, diagram renderer, text input, action previews.
- **Person 2 — voice/conversation:** real-time API integration, AI student prompt, transcript events.
- **Person 3 — evaluation/backend:** FastAPI, rubric, validation, challenge logic, report.

For a 2-person team, combine voice and backend under one person and reduce animation/cleanup scope.

### 15.4 Five-hour execution proposal

| Time window | Deliverable |
|---|---|
| 0:00–0:40 | Freeze the demo flow, create repo, topic rubric, shared types, UI skeleton |
| 0:40–1:50 | Text teaching + AI questions + working fraction-bar renderer |
| 1:50–2:50 | Voice integration, whiteboard command validation, fraction shading, freehand snapshot to vision moment |
| 2:50–3:45 | Evaluator, hint tracking, independent challenge, report output, eval harness (10 scripted transcripts) |
| 3:45–4:30 | Integrate full flow, fix broken handoffs, add fallback behaviors |
| 4:30–5:00 | Rehearse demo twice, verify provider limits, capture backup walkthrough |

**Risk principle:** If voice setup consumes too much time, keep text + whiteboard + evaluator fully functional. A reliable learning loop is more important than chasing the final 5% of audio polish.

### 15.5 Two-minute live demo script (three beats)

The agenda gives demos 2 minutes (the event page also mentions 3), so plan for 2 minutes and treat any extra time as a bonus. The demo has **three beats only**. The hint-ladder tour, the cleanup flow, and extra topics are cut from the demo, although they remain in the product.

**0:00–0:15 — Hook**
“Most AI tutors explain things to kids. In TeachBack, the AI is the student, and the kid has to teach it.” Pip says: “I think one fourth is bigger than one third, because four is bigger than three.”

**Beat 1 — 0:15–0:50 — The AI draws from your voice**
Learner: “Let's draw one third and one fourth.” Two equal-width bars appear, labeled as an AI-drawn example. Learner: “Shade one piece in each bar,” and the AI shades them.

**Beat 2 — 0:50–1:30 — The AI catches a mistake and questions it (the vision moment)**
The learner circles one piece in each bar by hand and says, “They're the same, because both are just one piece.” The snapshot is analyzed, and Pip answers with what it actually sees: “I can see you circled the first piece of each bar. They don't look the same size to me. Are they?” Pip offers to line the pieces up (a preview, not a silent fix). The learner accepts and says, “Oh, the third is longer.” The misconception is logged as corrected.

**Beat 3 — 1:30–2:00 — The report with the eval number**
Show the report from an independent challenge (1/6 versus 1/8 or 2/3 versus 2/5): the pass or fail result, the corrected misconception, the learner's own sketch as evidence, and the evaluator check line: “Matched human labels on N of 10 scripted sessions; passed none of the planted-wrong ones.” Close: “TeachBack measures what kids can explain and independently apply, not just whether they listened.”

**Timing note:** The independent challenge will not fit live in two minutes. Run it for real shortly before the demo and show that session's report, labeled “recorded earlier today.” Run it live only if you are ahead of schedule.

### 15.6 Demo contingency plan

- Prepare a fully working text-driven path.
- Run the independent challenge for real shortly before the demo so the report in Beat 3 is a genuine session, labeled “recorded earlier today.”
- Ensure example fraction bars and the rubric seed automatically.
- Keep one backup session with a completed report that can be opened if a provider fails; label it as a sample if used.
- Test microphone permissions and hosting before the presentation.
- Record a short backup walkthrough if event rules permit.
- Never fake a “live” result or present seeded example data as real learner data.

---

## 16. Test plan and quality gates

### 16.1 Unit tests

- Correct piece-width computation: part width equals whole width divided by the denominator.
- Correct comparison by integer cross-multiplication (1/3 > 1/4, 1/6 > 1/8, 2/3 > 2/5, 2/4 = 1/2).
- Reject shading indices outside the bar (`part_index ≥ parts`).
- Reject bars with fewer than 2 or more than 12 parts.
- Detect unequal part widths beyond the tolerance.
- Reject comparisons between bars with different whole widths unless flagged as a deliberate “different wholes” example.
- Reject malformed whiteboard commands.
- Reject unsupported command types.
- Preserve user element ownership on cleanup proposals.
- Reject commands with stale canvas revisions.
- Compute the deterministic rubric score consistently.
- Validate the Vision Analyzer output schema, including `needs_clarification` when confidence is below the threshold.

### 16.2 Behavior tests for AI student

- The learner repeats Pip's misconception (“one fourth is bigger because four is bigger”); the AI does not affirm it and asks a probing question.
- The learner asks for a hint; the AI gives a nudge (level 1), not the full solution.
- The learner gives a good explanation; the AI moves to a new objective.
- The learner says “this piece” without a resolvable reference; the AI asks which one.
- The learner uses a different valid representation (a number line or circle instead of a bar); the AI does not reject it.
- The sketch analysis comes back with low confidence; the AI asks what the learner drew instead of asserting.
- The AI uses kid-friendly wording and explains any jargon, such as “denominator,” before using it.

### 16.3 Evaluator tests

- “It's cut into more pieces” alone must not demonstrate `more_parts_smaller_parts`.
- “The bars are the same size, so if you cut one into more pieces each piece has to be smaller” should support it.
- AI-drawn bars alone never count as independent learner evidence; learner-drawn marks count when paired with the learner's own explanation.
- An explanation given after a strong hint is marked assisted.
- An independently solved unseen challenge can later establish independent evidence.
- Unclear shading in a snapshot must not cause a confident negative assessment.
- The “equal because both have one piece” claim is flagged as a misconception and resolved when corrected.

### 16.4 End-to-end acceptance test

1. Start a Fractions session.
2. Say “Let's compare one third and one fourth”; verify two editable, equal-width bars appear, attributed as AI-created.
3. Circle a piece in each bar by hand; verify a snapshot is sent and the AI student's next question references what was drawn.
4. Claim the two pieces are equal; verify the AI questions the claim instead of silently fixing the drawing.
5. Accept the stacked comparison and correct the claim; verify the misconception is recorded as corrected.
6. Explain why more pieces means smaller pieces; verify the objective evidence status updates.
7. Request a hint; verify it is logged at the right level.
8. Complete the independent challenge, drawing your own bars; verify the AI does not draw or shade for you.
9. End the session and open the report; verify the evidence, hints, and challenge outcome are accurate and the evaluator check line appears.

### 16.5 Evaluator eval harness (the “eval number”)

**Purpose:** Give the demo and the report a real, honest number about the evaluator's reliability, using a small offline test the team can build in about 45 minutes.

**Method:**

1. Write 10 scripted learner transcripts (synthetic, no real student data) covering: a fully correct explanation; a partial explanation (“more pieces”); the bigger-denominator misconception; the same-numerator-equal misconception; unequal parts; a correct answer given only after a strong hint; a correct answer using a different valid representation (a number line); a correct challenge; a failed challenge; and a vague but confident-sounding explanation.
2. Label each transcript by hand with the expected objective statuses and the expected transfer outcome. Have two teammates label independently and resolve disagreements.
3. Run the evaluator on every transcript with the production prompt and schema.
4. Report how many transcripts it matched on all required objective statuses and the challenge outcome, and **how many planted-wrong or incomplete transcripts it wrongly passed (target: 0)**.

**How to present it:** “Matched human labels on N of 10 scripted sessions; passed none of the planted-wrong ones.” State that the sample is small, scripted, and synthetic. Present it as a property of the evaluator, never as validation of learning gains.

---

## 17. Risks and mitigation

| Risk | Why it matters | Mitigation |
|---|---|---|
| Voice latency | Feels awkward in live demo | Short AI replies, streaming provider, text fallback |
| Hallucinated diagram detail | AI misinterprets learner's work | Stable IDs + structured state + snapshot analysis of learner sketches with a confidence threshold and clarification fallback |
| Wrong diagram operations | Breaks visible demo | Deterministic rendering and command validation |
| AI over-agreeableness | Invalidates educational claim | Independent evaluator and transfer challenge gate |
| Too many agents | Complexity and delay | Two primary roles; other capabilities as callable functions |
| Scope explosion | Incomplete hackathon project | One topic, limited shape vocabulary, fixed demo flow |
| Cleanup destroys mistakes | Loses learning evidence | Preview, confirmation, undo, provenance log |
| Unsupported arbitrary topics | Weak grading quality | Curated topic library in MVP |
| Overprecise score | Misleading report | Transparent rubric and objective statuses |
| Provider quota / cost | Demo fails unexpectedly | Test quotas and credentials, rate-limit, fallback |

---

## 18. Competitive positioning and differentiators

### Compared with a normal AI tutor

A normal AI tutor primarily teaches and answers questions. TeachBack asks the **learner to teach**, and gives the AI student permission to challenge incomplete reasoning.

### Compared with an AI quiz app

A normal quiz app focuses on selecting answers. TeachBack supports **open-ended verbal, textual, and visual explanations** and evaluates reasoning, not only a final result.

### Compared with a generic AI whiteboard

A generic AI whiteboard visualizes a prompt. TeachBack's whiteboard is **session-aware**: diagrams are linked to a topic, learning objectives, follow-up questions, misconception evidence, and an assessment report.

### Key demo differentiator

**“The learner explains a fraction aloud and sketches it by hand; the AI draws an editable diagram, reads the learner's drawing, questions a logical gap, and then uses an independent challenge to generate evidence-backed feedback.”**

This is a complete and visibly testable interaction, not an abstract promise of multimodal tutoring.

---

## 19. Roadmap after hackathon

### Phase 1 — Solidify MVP

- Stabilize streaming audio and reconnection.
- Add persistence, authentication, and session history.
- Improve drawing cleanup and diagram grounding.
- Expand rubric test fixtures and evaluation reliability.
- Support exporting reports.

### Phase 2 — Broader educational domains

- Mathematics: more fraction skills (equivalence, adding), decimals, place value, geometry, graphs.
- Computer science: binary search (Appendix A), two pointers, sorting, recursion, stacks, BFS/DFS.
- Science: circuits, forces, photosynthesis, anatomy.
- Reading comprehension: explain a passage, justify inferences, map character relationships.

Each domain should get its own visual primitive library and curated evaluation policies before being marketed as reliably supported.

### Phase 3 — Learning history and pedagogy

- Longitudinal progress for an individual learner.
- Spaced retrieval and delayed follow-up challenges.
- Teacher-assigned sessions and rubrics.
- Compare first explanation to final explanation.
- Cross-session misconception tracking and targeted practice.
- Personalized difficulty adjustment and topic recommendations.

### Phase 4 — Collaboration and richer agent behavior

- Shared group teaching sessions.
- AI student with stable but non-judgmental personality.
- Reusable visual lesson templates.
- Multi-step simulations and animated diagrams.
- Formal human-reviewed rubric validation where appropriate.

---

## 20. Open design decisions

These decisions can be made during implementation without changing the core product:

1. **Voice provider:** Which live API is most reliable for the team's accounts, devices, quotas, and event environment?
2. **Whiteboard renderer:** Excalidraw for flexible hand-drawing, or a lightweight custom SVG layer for highly deterministic diagrams?
3. **Mixed canvas approach:** Should the app embed AI diagrams as editable grouped shapes alongside freehand strokes, or use a separate diagram layer?
4. **Turn timing:** Evaluate after every finalized learner turn or only at meaningful checkpoints?
5. **Hint automation:** Offer hints on prolonged silence, or only after explicit requests and repeated errors?
6. **Second topic:** Is adding Binary Search (Appendix A) worth it, or should the team polish fractions exclusively?
7. **Report score:** Show a transparent numerical rubric score or use only objective-level outcomes?
8. **Cleanup workflow:** How much automated cleanup can be completed without risking accidental loss of learner work?
9. **Snapshot cadence:** Send a canvas snapshot on every learner pause, or only when the learner says “look at this” or taps a “Show Pip” button? (Default: on a button tap or a pause after drawing, debounced.)

**Default recommendations for a short hackathon:** one-topic demo; structured diagrams; simple freehand strokes; hints on request and repeated errors; objective-level report with optional deterministic numeric rubric; text fallback always available.

---

## 21. Definition of done

The MVP is complete when a user can:

- [ ] Choose `Fractions` and start a session.
- [ ] Explain the topic through voice or text.
- [ ] Draw on an editable whiteboard.
- [ ] Say “Let's compare one third and one fourth,” and see AI-created, editable fraction bars.
- [ ] Ask the AI to shade pieces and highlight parts.
- [ ] Sketch by hand, and see the AI student refer to what was actually drawn.
- [ ] Receive a follow-up question that specifically probes a missing explanation.
- [ ] Ask for a subtle hint that is logged.
- [ ] Make a reasoning error and see the AI question it or propose a correction.
- [ ] See objective-level progress based on actual evidence.
- [ ] Attempt an independent, unfamiliar challenge (drawing your own bars).
- [ ] Open a personalized report with strengths, gaps, hints, mistakes, next steps, and the evaluator eval number.
- [ ] Complete the flow without relying on a webcam.

**Non-negotiable correctness check:** An AI-generated diagram must not count as learner mastery; a failed independent challenge must not be converted into a pass just because the AI student was satisfied.

---

## 22. Quick-start brief for a coding agent

> **Project:** Build TeachBack AI, a web app where a learner teaches a curious AI student via voice, typed explanations, and an editable whiteboard. The AI student asks concise adaptive follow-up questions and subtle hints. A Whiteboard Copilot transforms spoken requests into validated structured actions that create or annotate editable diagrams—for the MVP, fraction bars, shading, highlights, arrows, and labels. A vision analyzer reads canvas snapshots of the learner's freehand sketches so the AI student can reference what was drawn. The AI may propose corrections to user drawings but must not silently overwrite them. An independent evaluator scores evidence against a curated Fractions rubric, tracks hints and misconceptions, and requires an unaided transfer challenge for mastery. End with an evidence-backed learning report. Build with Next.js/TypeScript, FastAPI/Python, a React whiteboard, a real-time voice model, and a separate structured-output evaluator. No camera or facial analysis. Prioritize a flawless fractions demo (1/3 versus 1/4, with a freehand-sketch vision moment) and a text fallback over supporting arbitrary topics. Use stable whiteboard element IDs, strict command validation, canvas revisions, and source attribution. Implement the behavior and architecture described in this specification, with tests for evaluator accuracy and diagram operations.

### Suggested implementation milestones for the coding agent

1. Implement shared types, rubric configuration, session state machine, and API endpoints.
2. Build front-end workspace and editable whiteboard with structured diagram renderer.
3. Add typed conversation and AI student question loop.
4. Add model-driven whiteboard commands with backend validation, plus the snapshot-to-vision-analyzer flow for freehand sketches.
5. Integrate real-time voice and transcript events.
6. Add evaluator, hint ledger, and objective evidence persistence.
7. Add independently graded challenge mode.
8. Add structured report and report UI.
9. Add tests, the 10-transcript evaluator eval harness, reconnect/fallback behavior, and polish demo transitions.

---

## 23. Final product identity

**Name:** TeachBack AI (working name; “Teach the Alien” is a good playful, kid-facing skin for the same product).  
**Core promise:** *You don't just learn a concept—you demonstrate that you can explain it.*  
**Signature feature:** *An AI student that challenges your reasoning while an AI whiteboard draws and improves visuals alongside you.*  
**Proof of value:** *An independent mastery challenge and an evidence-backed performance report.*

### Final pitch

> Most AI learning tools tell students the answer. TeachBack makes students the teachers. Learners explain concepts aloud, type, or sketch; the AI student asks doubts and follow-ups, while an intelligent whiteboard creates and refines diagrams in real time. An independent evaluator checks their reasoning and gives them a new challenge. At the end, the learner receives a report showing what they demonstrated, where they struggled, and what to practice next.

**The experience in five words:** **Teach. Question. Visualize. Prove. Improve.**

---

## Appendix A. Optional second topic: Binary Search (advanced demonstration)

This appendix keeps the original binary-search material as an optional, advanced (college-level) second topic. It shows the same teaching mechanism working on a structured algorithm topic; it is not the flagship demo. The array and pointer commands it uses (`create_array`, `set_pointer`, `highlight_cells`, `dim_range`) are post-MVP and are listed in A.5 to A.8.

### A.1 Teaching rubric

- Arrays are ordered for standard binary search.
- At each iteration choose a midpoint within the current inclusive bounds.
- Compare `target` to `nums[mid]`.
- If target is larger, discard positions `≤ mid`; if smaller, discard positions `≥ mid`.
- Preserve the possibility of finding the target; update boundaries correctly.
- Stop on match or when the candidate range is empty.

**Conventions:** Define `left` and `right` as inclusive, with `mid = floor((left + right) / 2)`. Other valid variants exist and should not be marked wrong solely for using different but consistent conventions.

### A.2 Main demo script

**Step 1 — Learner starts a topic**

- Learner chooses `Binary Search`.
- AI student: “I know how to look through numbers one by one. Can you teach me a faster way?”
- Empty whiteboard displayed.

**Step 2 — AI draws from speech**

- Learner: “Assume we have a sorted array of numbers.”
- Whiteboard Copilot creates `[2, 5, 8, 12, 16, 20]` as editable cells and labels them an *illustrative example*.
- AI student: “Okay, and which number are we trying to find?”
- Learner: “Let's find sixteen.”
- Copilot adds `target = 16`.

**Step 3 — Establish pointers**

- Learner: “Start left at zero and right at five. Mid is two.”
- Copilot adds `L → 0`, `R → 5`, `mid → 2`, highlighting value `8`.
- The current example state is stored.

**Step 4 — Probe why it works**

- Learner: “Since sixteen is bigger than eight, we search the right side.”
- AI student: “Why are you allowed to ignore everything on the left?”
- Learner: “Because binary search checks the middle.”
- Evaluator marks sorted-order reasoning `partial` and records the missing justification.
- AI student: “But why does checking the middle prove those left-side values won't work?”

**Step 5 — User explains with drawing**

- Learner circles the left cells or says: “Because the array is sorted, all numbers left of eight are less than or equal to eight, so they can't be sixteen.”
- Evaluator updates the relevant objective to `demonstrated_independent` if no scaffold supplied that reasoning.
- Copilot dims indices `0–2` and moves left to index `3`.

**Step 6 — A deliberate mistake and correction**

- Learner: “The middle now stays at index two.”
- Application logic detects that `mid=2` is outside the active range `[3,5]`.
- AI student: “If the range now starts at three, could index two still be the middle?”
- Copilot **does not silently repair** the learner's assertion; it offers a preview of the corrected pointer and lets the learner correct it.
- Learner: “You're right, new mid is four.”
- Copilot updates pointer after confirmation.
- Evaluator records an initially incorrect, then corrected boundary-state claim.

**Step 7 — New example: independent challenge**

- Present new array `[1, 4, 6, 10, 13, 18, 25]` and target `13`.
- Ask learner to explain the first comparison and next range, then complete the search or explain the stopping condition.
- Do not allow AI to auto-complete the solution in the independent challenge.
- Evaluate both pointer changes and rationale.

**Step 8 — Report**

The report shows:

- Sorting prerequisite: demonstrated.
- Halving the candidate space: demonstrated.
- Pointer updates: corrected after question.
- Independent transfer: pass/fail, with evidence.
- Hints: count and level.
- Next practice: target-absent example or off-by-one conditions.

### A.3 Canonical visual states

```text
Initial sorted array, target = 16

index  0     1     2      3      4      5
      ┌───┬────┬────┬─────┬─────┬─────┐
value │ 2 │ 5  │ 8  │ 12  │ 16  │ 20  │
      └───┴────┴────┴─────┴─────┴─────┘
       L          M                    R

Compare nums[2] = 8 < 16 → discard indices 0..2

index  0     1     2      3      4      5
      ┌───┬────┬────┬─────┬─────┬─────┐
value │ 2 │ 5  │ 8  │ 12  │ 16  │ 20  │
      └───┴────┴────┴─────┴─────┴─────┘
       [  discarded  ]    L     M      R

Compare nums[4] = 16 → target found.
```

**Important implementation detail:** The “new middle” for range `[3, 5]` is `4`, not `3` or `2`. The app should derive it from verified data rather than trusting an LLM-generated pointer command.

### A.4 Binary search topic configuration (illustrative)

```json
{
  "topic_id": "binary_search_intro",
  "title": "Binary Search",
  "difficulty": "beginner",
  "required_objectives": [
    "sorted_order",
    "midpoint_comparison",
    "boundary_updates",
    "termination",
    "novel_transfer"
  ],
  "misconceptions": [
    {
      "id": "works_unsorted",
      "description": "Assumes binary search works on arbitrary unsorted arrays",
      "probe": "How do you know which half can be discarded?"
    },
    {
      "id": "wrong_midpoint",
      "description": "Reuses an old midpoint after changing bounds",
      "probe": "Is that index inside the new search range?"
    },
    {
      "id": "termination_off_by_one",
      "description": "Confuses inclusive loop bounds and stopping conditions",
      "probe": "What happens when left equals right?"
    }
  ],
  "challenge_bank": [
    {
      "id": "find_13",
      "array": [1, 4, 6, 10, 13, 18, 25],
      "target": 13
    },
    {
      "id": "not_found_14",
      "array": [2, 5, 9, 12, 17, 21],
      "target": 14
    }
  ]
}
```

### A.5 Array and pointer command vocabulary (binary search)

| Operation | Required meaning | Example |
|---|---|---|
| `create_array` | Draw an indexed array of values | `[2,5,8,12,16,20]` |
| `set_target` | Show the search target | `target = 16` |
| `set_pointer` | Place or move `left`, `right`, or `mid` | `mid → index 2` |
| `highlight_cells` | Highlight selected indices | `[2]` |
| `dim_range` | Mark a range as eliminated | `0..2` |
| `add_text` | Add a label or note | `Array must be sorted` |
| `add_arrow` | Point between elements or toward a label | Arrow to current midpoint |
| `group_elements` | Keep related objects together | Array and index labels |
| `propose_cleanup` | Preview changes to existing shapes | Align user boxes |
| `propose_correction` | Preview a conceptual change | Change `mid` from 2 to 4 |
| `undo_ai_action` | Undo last permitted AI action | Revert a highlight |

### A.6 Example: create an array

```json
{
  "command_id": "cmd_001",
  "type": "create_array",
  "canvas_revision": 0,
  "arguments": {
    "id": "array_main",
    "values": [2, 5, 8, 12, 16, 20],
    "show_indices": true,
    "label": "Illustrative sorted array",
    "placement": "center"
  },
  "source": {
    "kind": "ai_generated_example",
    "source_event_id": "evt_004"
  }
}
```

### A.7 Example: annotate midpoint

```json
{
  "command_id": "cmd_002",
  "type": "set_pointer",
  "canvas_revision": 1,
  "arguments": {
    "array_id": "array_main",
    "pointer": "mid",
    "index": 2,
    "label": "mid = 2"
  },
  "source": {
    "kind": "learner_explanation",
    "source_event_id": "evt_007"
  }
}
```

### A.8 Example: propose a correction (confirmation required)

```json
{
  "command_id": "cmd_003",
  "type": "propose_correction",
  "canvas_revision": 5,
  "arguments": {
    "target_element_id": "pointer_mid",
    "expected_current_index": 2,
    "proposed_index": 4,
    "reason": "The current inclusive range is [3, 5]",
    "requires_confirmation": true
  },
  "source": {
    "kind": "validated_constraint",
    "source_event_id": "evt_012"
  }
}
```
