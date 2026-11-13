# Curio — TeachBack AI

Version 1.3 · Curio’s rediscovery adventure

Curio is a playful learning-by-teaching app for children ages 8–12. Its companion is a small retro television with animated eyes, big expressive eyebrows, antennae, tiny feet, and a few loose screws. Once he knew everything—but his rattly hardware has scrambled the connections between his memories. Familiar ideas still flicker on his screen; he needs a patient young teacher to help the reasons click back into place.

The learner’s mission is to help Curio remember through words, voice and drawings. He asks a specific question, listens, tries to put the explanation into his own words, and occasionally celebrates a connection coming back. For now, his rediscovery adventure supports mathematics only; physics and other subjects are future chapters. Fractions remain the flagship demo.

Read the full [character and interaction guide](CURIO_CHARACTER.md). The shared persona profile drives the welcome, hints, challenge invitation, and story dialog; a common behavior contract is included in text, native voice and sketch-analysis prompts. Facial expressions show interaction state, never a mastery verdict or an inferred child emotion.

The original TeachBack v1.1 requirements remain the baseline in [TeachBack_AI_Product_Spec_v1.1.md](TeachBack_AI_Product_Spec_v1.1.md). This addendum replaces the Pip/alien persona with Curio and establishes the visual direction.

## Experience and visual language

Warm paper backgrounds, dark green ink, a worn-blue Curio with gold glasses and red antenna tips, restrained lime accents, clear borders, generous whitespace, and readable typography. A small TV logo and Curio’s expressive silhouette supply the personality. The workspace uses practical drawing tools; reports use a clean conversation list and a quieter reading layout instead of nested dashboard cards. Use supportive, short, age-appropriate language. The learner should feel invited to explore rather than tested. Provide readable contrast, keyboard focus, responsive layouts, touch drawing, reduced-motion support, and labeled controls.

Curio states: idle (gentle blink), listening (attentive eyebrows), searching his memory (asymmetric eyebrow and gently wobbling loose screw), speaking (subtle mouth movement), questioning (tilt), and encouraging (warm expression). Expressions must never substitute for evidence-based evaluation.

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

## Conversation scope update

Curio accepts questions and explanations about any mathematics topic. It answers direct math questions with concise explanations and stays in the curious student role when the learner teaches. Fractions remain the default demo, curated topic, whiteboard example, hint ladder and independent practice challenge. General math conversations do not imply subject-specific assessment support. Non-math requests are redirected toward mathematics.

## Implementation update — connected whiteboard actions

Curio now emits schema-constrained fraction creation and shading commands with conversational replies. The backend validates the complete command batch before committing the turn and diagram together. Each bar has a stable ID, ownership and source event; the board has a monotonic revision, undo snapshots and a visible last-action message. Explicit slash fractions must match the requested numerator and denominator exactly. AI cannot silently replace bars, modify partitions, erase learner strokes, or draw during independent practice. UI controls use the same validated backend path, and bar shading persists in SQLite. Four equal-width bars and denominators up to 24 are supported. Learners may toggle individual pieces or undo bar edits independently from freehand strokes. Snapshot vision and independent grading remain pending.

## Implementation update — broader mathematics drawing

Curio can compose number lines, coordinate diagrams, geometry and equations from bounded 2D line/arrow/circle/polygon/text primitives. Each element has a stable ID; selection controls support movement and text-label editing with undo. Function-graph commands supply an expression and coordinate ranges; a backend AST allowlist computes 401 samples without eval, arbitrary calls or executable model code. Undefined values and large visual jumps split graph segments. All diagram commands share revision checks, source metadata, persistence, atomic batches and independent-practice restrictions. One general diagram or up to four fraction bars fits at once. Geometry remains illustrative; finite plots are not symbolic proofs. Freehand vision, 3D rendering and universal mathematical notation remain outside the current renderer.

## Requested behavior update — clear and redraw

Learners may ask Curio to erase the board or start a new drawing without using the manual clear button. This explicitly authorizes a structured clear followed by the new drawing in the same atomic batch; Curio describes the clear in its response. This replaces the earlier requirement to request manual clearing on an occupied board. Additive requests and existing-element edits retain the board. Clear actions carry an ID so the client removes only the submitted pen-stroke snapshot once; newly drawn strokes survive pending requests and retries. Diagram undo restores the previous clear ID and diagrams, and the browser restores cleared strokes where available in current-tab memory. Independent practice restrictions still apply.

## Implementation update — snapshot-based sketch understanding

Show Curio captures the board SVG as an actual PNG, including learner strokes and structured diagrams. A separate Gemini vision function returns bounded observations, known element/part references, confidence, clarification state and a concise grounded reply. The backend checks image format/size/dimensions, canvas revision and element references; confidence below 0.75 or an invalid reference forces clarification. This threshold is an implementation heuristic, not a calibrated assessment measure. Snapshot requests are idempotent, do not modify drawings, and never change mastery status. Challenge snapshots remain descriptive and ask for learner reasoning without hints or a pass/fail claim. Raw images are transient provider inputs; hashes, revisions and observations persist as session events. Subsequent text turns may use observations only while structured and freehand revisions still match. The interface flags newer drawings and allows explicit re-sharing. No webcam is involved.

## Implementation update — native live voice before evaluation

Evaluation remains deferred. Curio now supports microphone input and native streamed Gemini Live audio through a FastAPI WebSocket relay, with backend-only keys. Live transcripts share canonical session history with typed messages; reconnect seeds that history and the current diagram state. Spoken whiteboard operations use the same validated command path and source attribution. The UI provides visible connection/listening/speaking states, mute, playback stop, end, and a text fallback. Provider interruption events stop queued playback and preserve partial transcript events as interrupted. Tool-call turn boundaries are kept with their spoken follow-up rather than prematurely splitting the learner’s request. The microphone and audio contexts are released on end, failure or unmount. Text/lesson/snapshot mutations require ending voice first to preserve ordering; drafts and pen drawing remain available. Voice snapshots are treated as historical; Show Curio remains the explicit current-sketch analysis path. Audio is transient; transcripts and diagram changes persist. This local version supports one active voice connection per session and manual reconnect, with a 14-minute connection cap. Independent-practice drawing/hint restrictions continue to apply, and voice never awards mastery.

## Character behavior update

Curio’s forgotten knowledge is a fictional framing for learning by teaching. He remembers actual conversation context, avoids repetitive fake amnesia, and occasionally paraphrases a sound learner explanation as a connection returning. He answers direct math questions accurately and probes mistakes gently instead of intentionally teaching false facts. Character questions are welcome; physics and other subject lessons remain future scope. A child’s effort never becomes a duty to fix him, and memory-themed reactions never count as mastery. Infrastructure failures are explained honestly rather than disguised as memory glitches. Existing transcripts remain unchanged; the new persona applies to subsequent replies and new session greetings.

## Implementation update — conversation reports before exact metrics

`/reports` lists every persisted conversation, searchable across the saved transcript. Each detail page presents an ungraded result, exact learner contributions alongside Curio’s follow-ups, hints shared before a contribution, practice context and full text/voice/sketch history. The explanation review exposes evidence for a parent/teacher to inspect; it does not infer understanding from word counts, Curio’s enthusiasm or a correct-looking answer. Exact metrics and independent evaluation remain deferred.

Board outputs now have an append-only archive separate from the live undo stack. Requested clears and undo actions do not remove previously archived drawings. Newly shared sketch PNGs are stored locally in SQLite and served by a conversation-scoped image endpoint for the report; this supersedes the earlier transient-only snapshot policy. Historical images that were never retained remain unavailable, and old board states are labeled as recovered rather than a complete archive. Voice output is available as its saved transcript, without audio recordings. New conversations retain older reports, and any report can resume its corresponding session.

## Interface update — new conversations instead of independent practice

The independent-practice card and workspace entry control are removed for now. A New conversation action occupies their place in the report sidebar and beside the workspace hint button. The previous session remains available in Reports. Opening an older session that is still in challenge mode returns it to exploration through the existing backend transition, so drawing and hints remain usable. Historical transcripts and stored practice events are preserved; evaluation remains deferred.

## Visual direction update — clean and playful

The workspace, report list, report details, story dialog and missing-page state now share a compact TV wordmark, Bricolage Grotesque headings, DM Sans body text, warm paper, dark green ink and restrained yellow/lime accents. Purple gradients, sparkle decoration, backend/demo badges and stacked rounded-card layouts are removed. Playfulness comes from Curio, slightly tilted conversation icons and drawing tools rather than decorative UI copy. Report content uses a list, simple tabs, readable transcripts and actual drawing previews. The fixed teaching viewport and internal report scrolling remain, with desktop, compact-screen and mobile layouts. Focus indicators and reduced-motion support remain available.

## Avatar reference update

Curio’s avatar now follows the supplied blue-TV reference: a worn blue cabinet, heavy dark outlines, round gold glasses, yellow eyes, cream eyebrows, red antenna tips, a yellow antenna dome and front controls. The cabinet recedes to the right so his face and pupils look left toward the whiteboard. The implementation is an animated SVG with separate eyes, eyebrows, mouth and loose-screw groups, preserving blink, thinking, listening, speaking and reduced-motion behavior. The logo uses the same blue-TV identity.


### Teacher report overview — evaluation handoff
The report overview uses the supplied Comparing Fractions rubric: verdict, four
computed summary numbers, before/after objective statuses, learner quotes,
misconceptions with correction evidence, and next steps. Evaluation is requested
from the report after a conversation, runs once per unchanged transcript, and is
saved with the session. Continuing the conversation requires a fresh evaluation.
Chat history and drawings/sketch archives remain available in their existing tabs.
Quotes are checked against learner events; Curio responses cannot supply evidence.
The demo has no transfer task, so it cannot claim mastery. Other math topics remain
open for conversation but are not covered by this fractions rubric. A separately
selected synthetic sample is always labeled and never replaces a failed live result.
