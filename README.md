# Curio

A curious little TV you teach with words and drawings. Kid-friendly TeachBack AI, starting with fractions.

## Run locally

Requires Node.js 22.18+ and npm (including the TypeScript test runner).

```sh
npm install
npm run dev
```

Open http://localhost:3000. The client currently runs independently in an explicitly labeled local demo mode. No API credentials are required. Explanations remain in React memory and reset on refresh. Speech playback uses the browser's speech synthesis; voice input and model inference are not yet connected.

Optional API foundation (Python 3.11+):

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs. The UI does not call this foundation service yet.

## Checks

```sh
npm test
npm run typecheck
npm run build
```

## Product and implementation

Read [Curio product direction](docs/PRODUCT_SPEC.md) and the [original TeachBack spec](docs/TeachBack_AI_Product_Spec_v1.1.md). The current slice includes the animated TV avatar, responsive workspace, freehand drawing, editable fraction examples, scripted conversation, hints and a practice journal. Live voice, vision, independent evaluation, persistence, and genuine mastery reporting remain implementation milestones. The UI deliberately awards no mastery result.
