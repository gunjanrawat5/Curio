"""Curio teaching sessions. Run one local Uvicorn worker (per-session locks)."""
import asyncio
import os
import json
import hashlib
from copy import deepcopy
from typing import Literal
from pathlib import Path
from uuid import UUID, uuid4
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from backend.store import SessionStore, event, CHALLENGE
from backend.gemini import generate_reply, ProviderError
from backend.vision import CanvasSnapshot, analyze_sketch, grounded_analysis
from backend.whiteboard import CreateBar, ShadePart, DiagramCommand, BoardError, apply_commands

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
    canvas_revision: int | None = Field(default=None, ge=0)
    sketch_revision: str | None = Field(default=None, pattern=r'^[a-f0-9]{64}$')

class Action(BaseModel):
    request_id: UUID

class SketchTurn(Action):
    snapshot: CanvasSnapshot
    question: str = Field(default='Can you look at my drawing?', min_length=1, max_length=4000)

class BoardAction(Action):
    canvas_revision: int = Field(ge=0)
    operation: Literal['edit', 'clear', 'undo']
    commands: list[DiagramCommand] = Field(default_factory=list, max_length=8)

def get_session(session_id: UUID):
    session = app.state.store.get(str(session_id))
    if session is None:
        raise HTTPException(404, 'Session not found. Start a new session.')
    return session

def public(session):
    result = {k: v for k, v in session.items() if k != 'requests'}
    result['whiteboard'] = {k: v for k, v in session['whiteboard'].items() if k != 'history'}
    result['whiteboard']['can_undo'] = bool(session['whiteboard']['history'])
    return result

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
            board_context = {k: v for k, v in session['whiteboard'].items() if k != 'history'}
            latest = session.get('sketches', [])[-1:]
            if latest and latest[0]['canvas_revision'] == turn.canvas_revision == session['whiteboard']['revision'] and latest[0]['sketch_revision'] == turn.sketch_revision:
                board_context['vision_context'] = {**latest[0], 'current': True}
            reply = await generate_reply([*session['messages'], learner], session['phase'], board_context)
        except ProviderError as exc:
            raise HTTPException(exc.status, exc.message) from None
        if reply.commands:
            if turn.canvas_revision is None or turn.canvas_revision != session['whiteboard']['revision']:
                reply_text = "The board changed while we were talking. Please send that drawing request again."
            else:
                try:
                    session['whiteboard'] = apply_commands(session['whiteboard'], reply.commands, 'ai', learner['id'], session['phase'], text)
                    reply_text = reply.text
                except BoardError as exc:
                    # Do not echo a model's success claim when its commands were rejected.
                    reply_text = str(exc)
        else:
            reply_text = reply.text
        session['messages'].extend([learner, event('curio', reply_text)])
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
            session['whiteboard'] = {**session['whiteboard'], 'bars': [], 'diagrams': [], 'history': [], 'revision': session['whiteboard']['revision'] + 1, 'last_action': None}
            session['messages'].append(event('curio', CHALLENGE, 'challenge'))
        session['requests'][str(action.request_id)] = 'challenge'
        app.state.store.save(session)
        return public(session)


@app.post('/sessions/{session_id}/whiteboard')
async def edit_whiteboard(session_id: UUID, action: BoardAction):
    async with lock(session_id):
        session = get_session(session_id)
        fingerprint = 'board:' + json.dumps(action.model_dump(mode='json', exclude={'request_id'}), sort_keys=True)
        if already_done(session, action.request_id, fingerprint):
            return public(session)
        board = session['whiteboard']
        if action.canvas_revision != board['revision']:
            raise HTTPException(409, 'The board changed. Refresh it and try again.')
        if action.operation != 'edit' and action.commands:
            raise HTTPException(422, 'Undo and clear cannot contain drawing commands.')
        if action.operation == 'edit':
            try:
                board = apply_commands(board, action.commands, 'learner', str(action.request_id), session['phase'])
            except BoardError as exc:
                raise HTTPException(422, str(exc)) from None
        elif action.operation == 'clear':
            board = deepcopy(board)
            board['history'].append({'bars': deepcopy(board['bars']), 'diagrams': deepcopy(board.get('diagrams', [])), 'source': 'learner', 'source_event_id': str(action.request_id), 'commands': [], 'last_clear_id': board.get('last_clear_id')})
            board['last_clear_id'] = str(uuid4())
            board['bars'] = []
            board['diagrams'] = []
            board['revision'] += 1
            board['last_action'] = {'source': 'learner', 'description': 'You cleared the diagrams'}
        elif action.operation == 'undo':
            if not board['history']:
                raise HTTPException(409, 'No diagram actions to undo.')
            if session['phase'] == 'challenge':
                raise HTTPException(409, 'Previous examples cannot be restored during independent practice.')
            board = deepcopy(board)
            previous = board['history'].pop()
            board['bars'] = previous['bars']
            board['diagrams'] = previous.get('diagrams', [])
            board['last_clear_id'] = previous.get('last_clear_id')
            board['revision'] += 1
            board['last_action'] = {'source': 'learner', 'description': 'You undid the last diagram action', 'operation': 'undo'}
        session['whiteboard'] = board
        session['requests'][str(action.request_id)] = fingerprint
        app.state.store.save(session)
        return public(session)


@app.post('/sessions/{session_id}/explore')
async def explore(session_id: UUID, action: Action):
    """Leave independent practice explicitly, retaining all prior evidence."""
    async with lock(session_id):
        session = get_session(session_id)
        if already_done(session, action.request_id, 'explore'):
            return public(session)
        if session['phase'] != 'teaching':
            session['phase'] = 'teaching'
            session['messages'].append(event('curio', "We're back to exploring math together! I can help draw again. What would you like to put on the board?", 'explore'))
        session['requests'][str(action.request_id)] = 'explore'
        app.state.store.save(session)
        return public(session)


@app.post('/sessions/{session_id}/sketch')
async def show_sketch(session_id: UUID, turn: SketchTurn):
    try:
        image = turn.snapshot.decode()
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    image_hash = hashlib.sha256(image).hexdigest()
    fingerprint = 'sketch:' + hashlib.sha256(json.dumps({'image': image_hash, 'canvas_revision': turn.snapshot.canvas_revision,
        'sketch_revision': turn.snapshot.sketch_revision, 'stroke_count': turn.snapshot.stroke_count, 'question': turn.question}, sort_keys=True).encode()).hexdigest()
    async with lock(session_id):
        session = get_session(session_id)
        if already_done(session, turn.request_id, fingerprint):
            return public(session)
        if turn.snapshot.canvas_revision != session['whiteboard']['revision']:
            raise HTTPException(409, 'The board changed before Curio could look. Show the current sketch again.')
        if len(session['messages']) >= 120:
            raise HTTPException(409, 'This session is full. Please start a new session.')
        try:
            analysis = await analyze_sketch(image, turn.snapshot, session['whiteboard'], session['messages'], session['phase'], turn.question)
        except ProviderError as exc:
            raise HTTPException(exc.status, exc.message) from None
        analysis = grounded_analysis(analysis, session['whiteboard'])
        learner = event('you', turn.question, 'sketch')
        learner['snapshot'] = {'canvas_revision': turn.snapshot.canvas_revision, 'sketch_revision': turn.snapshot.sketch_revision, 'image_sha256': image_hash}
        observed = {**learner['snapshot'], 'event_id': learner['id'], 'created_at': learner['created_at'], 'stroke_count': turn.snapshot.stroke_count,
            'analysis': analysis.model_dump()}
        session.setdefault('sketches', []).append(observed)
        session['messages'].extend([learner, event('curio', analysis.reply, 'sketch_reply')])
        session['requests'][str(turn.request_id)] = fingerprint
        app.state.store.save(session)
        return public(session)
