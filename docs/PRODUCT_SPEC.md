# Curio — TeachBack AI

Version 1.2 · Implementation direction

Curio is a playful learning-by-teaching app for children ages 8–12. The child is the teacher, and Curio is their curious AI student: a small, friendly retro television with animated eyes, big expressive eyebrows, two antennae, and tiny feet. Curio blinks, tilts, listens, and reacts with curiosity. Its expressions communicate interaction state; they never imply a mastery verdict or infer a child's emotions.

The original TeachBack v1.1 requirements remain the baseline in [TeachBack_AI_Product_Spec_v1.1.md](TeachBack_AI_Product_Spec_v1.1.md). This addendum replaces the Pip/alien persona with Curio and establishes the visual direction.

## Experience and visual language

Warm cream backgrounds, lavender accents, butter-yellow Curio, rounded surfaces, generous whitespace, friendly typography, dotted drawing paper, and small celebratory details. Use supportive, short, age-appropriate language. The learner should feel invited to explore rather than tested. Provide readable contrast, keyboard focus, responsive layouts, touch drawing, reduced-motion support, and labeled controls.

Curio states: idle (gentle blink), listening (attentive eyebrows), thinking (asymmetric raised eyebrow), speaking (subtle mouth movement), questioning (tilt), and encouraging (warm expression). Expressions must never substitute for evidence-based evaluation.

## MVP contract

Fractions first: compare 1/3 and 1/4 using equal-sized wholes and equal parts. Voice and typing share one conversation. Editable AI fraction bars coexist with learner-owned freehand strokes. Drawing corrections require confirmation. A multimodal analyzer must actually inspect a snapshot before claiming to understand a sketch. Record evidence and hint levels independently from Curio's dialogue. Gate mastery on an unaided transfer challenge comparing 1/6 and 1/8, with a learner-created diagram and explanation. Reports cite actual evidence, identify assistance, and show a real evaluator benchmark only after running it. No camera.

## Initialized implementation

- Next.js / React / TypeScript web client with CSS/SVG Curio avatar.
- Editable SVG whiteboard: freehand pen, three colors, last-stroke undo, clear, structured same-width fraction bars, tap-to-shade mode.
- Local deterministic conversation preview, progressive hints, speech synthesis, transfer practice and an honest practice journal.
- FastAPI service foundation for curated topic discovery and health checks.
- Fraction validation and exact cross-product comparison, with unit tests.

## Remaining before MVP completion

1. Server-authoritative sessions, event persistence, canvas revisions, command provenance and correction proposals.
2. Real conversational provider, streaming audio and shared transcripts.
3. Snapshot export and real multimodal drawing analysis.
4. Independent structured evaluator, rubric evidence and challenge gating.
5. Evaluator ten-transcript harness, durable reports, reconnect behavior and end-to-end checks.

The initialized UI is explicitly a local demo. Scripted replies are not model evaluation. It must not award mastery, claim sketch understanding, fabricate benchmark numbers, or present AI diagrams as learner evidence.

## Implementation update — connected teaching loop

The frontend now creates and resumes FastAPI sessions. SQLite persists canonical messages, hint usage and practice phase. Gemini produces context-aware Curio replies using backend-only credentials; scripted conversation replies have been removed. Completed turns are committed atomically, and request IDs prevent duplicate turns on retry. The interface keeps unsent text on failures. Hint requests and the switch to independent practice preserve conversation history. Drawing remains local and is not sent to Gemini. Voice input, sketch analysis, independent grading and mastery reports remain pending. The service currently targets one local backend worker and has no public authentication layer.
