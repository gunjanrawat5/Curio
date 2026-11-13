"""Curio teaching sessions. Run one local Uvicorn worker (per-session locks)."""
import asyncio
import os
from pathlib import Path
from uuid import UUID
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from backend.store import SessionStore, event, CHALLENGE
from backend.gemini import generate_reply, ProviderError

load_dotenv(Path(__file__).resolve().parents[1] / '.env')

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = SessionStore()
    app.state.locks = {}
    yield

app = FastAPI(title='Curio API', version='0.2.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[s.strip() for s in os.getenv('FRONTEND_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')], allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])

class Turn(BaseModel):
    request_id: UUID
    text: str = Field(min_length=1, max_length=4000)

class Action(BaseModel):
    request_id: UUID

def get_session(session_id: UUID):
    session = app.state.store.get(str(session_id))
    if session is None:
        raise HTTPException(404, 'Session not found. Start a new session.')
    return session

def public(session):
    return {k: v for k, v in session.items() if k != 'requests'}

def lock(session_id):
    return app.state.locks.setdefault(str(session_id), asyncio.Lock())

def already_done(session, request_id, fingerprint):
    previous = session['requests'].get(str(request_id))
    if previous is not None and previous != fingerprint:
        raise HTTPException(409, 'This request ID was already used for a different action.')
    return previous is not None

@app.get('/health')
def health():
    key = os.getenv('GEMINI_API_KEY', '').strip()
    return {'status': 'ok', 'mode': 'gemini', 'provider_configured': bool(key and key != 'your_gemini_api_key_here'), 'evaluation_available': False}

@app.get('/topics')
def topics():
    return [{'id': 'fractions_intro', 'title': 'Fractions', 'ages': '8–12', 'objectives': ['equal_parts', 'same_whole', 'more_parts_smaller_parts', 'independent_transfer'], 'example': ['1/3', '1/4'], 'challenge': ['1/6', '1/8']}]

@app.post('/sessions', status_code=201)
def create_session():
    return public(app.state.store.create())

@app.get('/sessions/{session_id}')
def read_session(session_id: UUID):
    return public(get_session(session_id))

@app.post('/sessions/{session_id}/messages')
async def send_message(session_id: UUID, turn: Turn):
    text = turn.text.strip()
    if not text:
        raise HTTPException(422, 'Write an explanation first.')
    async with lock(session_id):
        session = get_session(session_id)
        fingerprint = 'message:' + text
        if already_done(session, turn.request_id, fingerprint):
            return public(session)
        if len(session['messages']) >= 120:
            raise HTTPException(409, 'This session is full. Please start a new session.')
        learner = event('you', text)
        try:
            # The caller cannot replace history or the system prompt.
            reply = await generate_reply([*session['messages'], learner], session['phase'])
        except ProviderError as exc:
            raise HTTPException(exc.status, exc.message) from None
        session['messages'].extend([learner, event('curio', reply)])
        session['requests'][str(turn.request_id)] = fingerprint
        app.state.store.save(session)
        return public(session)

@app.post('/sessions/{session_id}/hints')
async def hint(session_id: UUID, action: Action):
    async with lock(session_id):
        session = get_session(session_id)
        if already_done(session, action.request_id, 'hint'):
            return public(session)
        if session['phase'] == 'challenge':
            raise HTTPException(409, 'Hints are off during independent practice.')
        hints = ['Imagine two identical chocolate bars. What should stay the same to make a fair comparison?', 'Try dividing one whole into three equal pieces, and another into four. Compare just one piece.', 'More equal pieces of the same whole means each piece is smaller. Can you explain that in your own words?']
        session['messages'].append(event('curio', hints[min(session['hints'], 2)], 'hint'))
        session['hints'] += 1
        session['requests'][str(action.request_id)] = 'hint'
        app.state.store.save(session)
        return public(session)

@app.post('/sessions/{session_id}/challenge')
async def challenge(session_id: UUID, action: Action):
    async with lock(session_id):
        session = get_session(session_id)
        if already_done(session, action.request_id, 'challenge'):
            return public(session)
        if session['phase'] != 'challenge':
            session['phase'] = 'challenge'
            session['messages'].append(event('curio', CHALLENGE, 'challenge'))
        session['requests'][str(action.request_id)] = 'challenge'
        app.state.store.save(session)
        return public(session)
