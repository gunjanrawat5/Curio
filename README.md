# Curio

A curious little TV you teach with words and drawings. Kid-friendly TeachBack AI, starting with fractions.

## Setup

Requires Node.js 22.18+, npm, and Python 3.11+.

```sh
npm install
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Set these values in `.env` in the project root (copy `.env.example` if needed):

```dotenv
GEMINI_API_KEY=your_actual_key
GEMINI_MODEL=gemini-3.8-flash
```

The API key is read only by FastAPI. Never prefix the key with `NEXT_PUBLIC_`. Restart the backend after changing `.env`. The model is configurable to match the models available to your Gemini account. No scripted reply fallback is used.

## Run both services

Terminal 1 — frontend:

```sh
npm run dev
```

Open http://localhost:3000.

Terminal 2 — backend, from the same project directory:

```sh
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

Use one backend worker for this local build. API docs: http://localhost:8000/docs. Health: http://localhost:8000/health (`provider_configured` checks key presence, not validity).

Click **Let’s teach Curio**, type an explanation, and send. The backend supplies canonical conversation history to Gemini. Curio answers questions about any math topic and asks curious follow-ups when the learner teaches. Fractions remain the default demo; curated hints, diagrams and independent practice still cover fractions. Try “draw thirds and fourths”, “draw 2/3 and 2/5”, or “shade the second piece in the fourths bar”. Hints are recorded in that same history. Independent practice preserves the teaching history and disables hints; it is not graded yet. Sent messages appear immediately with a Curio typing indicator. You can draft the next message while waiting; failed messages stay in the conversation with a Retry button, and your next draft is preserved.

Sessions and hints persist in `backend/data/curio.sqlite3` (ignored by Git). The browser stores the current session ID in local storage so it can resume after refresh. Fraction bars and shading persist with the session; freehand strokes remain in tab memory. This is a local development app without authentication; do not expose it as a public service. Sending an explanation sends its conversation context to Gemini.

Optional configuration in the root `.env`:

- `NEXT_PUBLIC_API_URL` — browser API address, defaults to `http://localhost:8000`; restart Next.js after changes.
- `FRONTEND_ORIGINS` — comma-separated allowed browser origins; defaults to localhost and 127.0.0.1 on port 3000.
- `CURIO_DB_PATH` — alternate SQLite path.

## Checks

```sh
npm test
npm run typecheck
npm run build
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
python -m pytest backend/tests -q
```

Backend tests use a temporary database and mocked Gemini responses; they do not use API quota. Live Gemini verification needs a valid key and provider access.

## Product and implementation

Read [Curio product direction](docs/PRODUCT_SPEC.md) and the [original TeachBack spec](docs/TeachBack_AI_Product_Spec_v1.1.md). Implemented: animated avatar, drawing workspace, editable fraction examples, durable backend sessions, Gemini text dialogue, hint tracking, independent practice and a practice journal. Live voice, independent evaluation and mastery reporting remain milestones. Curio does not award mastery.

## Editable whiteboard actions

Gemini returns structured JSON with a reply and allowlisted create/shade commands. The backend validates fraction bounds (whole numbers, denominators 1–24, numerator no larger than denominator), exact explicitly written fractions, existing bar IDs, part indices, board capacity (four bars), canvas revision and independent-practice restrictions. A batch commits atomically with its conversation turn, with ownership and source event IDs. Equal-width geometry is computed by the SVG renderer rather than the model. Schema validation uses the [Gemini JSON Schema interface](https://ai.google.dev/gemini-api/docs/structured-output).

After drawing, the selection tool is enabled: tap a piece to shade or unshade it (keyboard Enter/Space also works). The displayed fraction follows the current shading. **Undo bars** restores the preceding bar action without touching pen strokes. The clear control removes bars and local strokes; bar changes are undoable. AI commands can add bars, change requested shading, or clear the board for a fresh drawing; they cannot silently change existing bar partitions. Ask Curio to start a new drawing to clear and replace the board automatically. General 2D geometry, number lines, equations and function graphs are also supported; freehand sketch analysis is available through Show Curio.

Structured bar state is sent to Gemini as context; learner freehand drawings are analyzed only when explicitly shared with Show Curio. Session recovery initializes missing board state for sessions created before this feature.

## Broader math diagrams

Try “draw a right triangle with labeled vertices”, “draw a number line from -3 to 3”, “draw a coordinate plane”, “show the quadratic formula”, or “plot y = x^2”. Curio emits bounded line, arrow, circle, polygon and text elements. Select the pointer tool, select an element, and use the small editor to move it or edit a text label. Undo restores diagram edits without erasing pen strokes.

Function graphs are sampled on the backend using an allowlisted expression interpreter: `x`, `pi`, `e`, arithmetic, constant powers from -12 to 12, and `sin`, `cos`, `tan`, `sqrt`, `abs`, `log`, `exp`. Model-generated code is never executed. Plots contain 401 samples with breaks at undefined/offscreen points; this is a finite visualization, not an exact symbolic graph. One general diagram or four fraction bars fit at once; Curio can clear and replace the board when you ask for a new diagram. When you request a fresh drawing, Curio announces the clear and replaces the old board. Shading, labeling, movement and explicit additive requests retain existing content. 3D scenes and arbitrary mathematical notation are outside this drawing vocabulary. Geometry is illustrative and not a measured proof.

If Curio says it cannot draw during a challenge, click **Back to exploring** in the practice banner above the chat. This explicitly ends independent practice and restores drawing and hints while preserving the session history; it does not mark the challenge as passed. **New puzzle** starts a fresh practice attempt.

Ask “clear the board”, “erase this and draw a triangle”, or “now draw a number line instead” to start fresh. Curio emits a validated `clear_whiteboard` followed by the creation command in one atomic batch. **Undo diagram** restores the preceding diagram and any cleared pen strokes still available in the current tab. Strokes drawn after submitting a request are retained, and retrying a completed clear does not erase them again. Independent practice continues to block AI drawing and clearing; use **Back to exploring** first.

## Sketch understanding

Draw with the pen, optionally type a question such as “what did I circle?”, then click **Show Curio** below the whiteboard. This captures only the board SVG, including its current diagrams and freehand strokes, as a 1200×810 PNG. No webcam, screen capture permission or file upload is used. The snapshot and question are sent to Gemini for visual analysis, with known diagram IDs and the current practice phase. The normal Send button continues the conversation; use Show Curio again after changing the drawing.

Curio references visible marks and asks a focused question. Low-confidence or ungrounded observations produce a clarification request. A small status indicates whether the drawing changed since the last shared snapshot. Vision cannot change the board and never awards mastery. In independent practice it may describe the sketch and ask for the learner’s reasoning without supplying a solution.

Snapshot requests validate PNG format, dimensions, size (2 MB), canvas revision and sketch identity. Retries are idempotent, and stale snapshots are rejected. Raw images are sent transiently to Gemini and are not stored in SQLite; the session stores image hashes, revision IDs, observations, uncertainty and the resulting conversation. Current sketch observations are supplied to later chat turns only if both the diagram revision and freehand-content hash still match.

Set `GEMINI_VISION_MODEL` optionally to choose a separate image-capable model; otherwise it uses `GEMINI_MODEL`. Install updated backend requirements and restart if needed.
