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

Click **Let’s teach Curio**, type an explanation, and send. The backend supplies canonical conversation history to Gemini and returns Curio's follow-up. Hints are recorded in that same history. Independent practice preserves the teaching history and disables hints; it is not graded yet. Sent messages appear immediately with a Curio typing indicator. You can draft the next message while waiting; failed messages stay in the conversation with a Retry button, and your next draft is preserved.

Sessions and hints persist in `backend/data/curio.sqlite3` (ignored by Git). The browser stores the current session ID in local storage so it can resume after refresh. Whiteboard strokes remain in tab memory. This is a local development app without authentication; do not expose it as a public service. Sending an explanation sends its conversation context to Gemini.

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

Read [Curio product direction](docs/PRODUCT_SPEC.md) and the [original TeachBack spec](docs/TeachBack_AI_Product_Spec_v1.1.md). Implemented: animated avatar, drawing workspace, editable fraction examples, durable backend sessions, Gemini text dialogue, hint tracking, independent practice and a practice journal. Live voice, sketch vision, model-driven diagram actions, independent evaluation and mastery reporting remain milestones. Curio does not award mastery.
