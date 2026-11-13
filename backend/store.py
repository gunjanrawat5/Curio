"""Small durable local session store. One atomic write per completed turn."""
import json
import os
import sqlite3
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from backend.whiteboard import empty_board
from backend.persona import PROFILE

GREETING = PROFILE['greeting']
CHALLENGE = PROFILE['challenge']

def event(role: str, text: str, kind: str = 'message') -> dict:
    return {'id': str(uuid4()), 'role': role, 'text': text, 'kind': kind, 'created_at': datetime.now(timezone.utc).isoformat()}

class SessionStore:
    def __init__(self, path: str | None = None):
        self.path = path or os.getenv('CURIO_DB_PATH', str(Path(__file__).parent / 'data' / 'curio.sqlite3'))
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS snapshots (sha256 TEXT PRIMARY KEY, png BLOB NOT NULL)')

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def create(self) -> dict:
        session = {'id': str(uuid4()), 'topic_id': 'fractions_intro', 'phase': 'teaching', 'messages': [event('curio', GREETING)], 'hints': 0, 'requests': {}, 'whiteboard': empty_board(), 'sketches': []}
        session['created_at']=session['messages'][0]['created_at']
        session['updated_at']=session['created_at']
        session['artifacts']=[]
        with self.connect() as db:
            db.execute('INSERT INTO sessions VALUES (?, ?)', (session['id'], json.dumps(session)))
        return session

    def get(self, session_id: str) -> dict | None:
        with self.connect() as db:
            row = db.execute('SELECT data FROM sessions WHERE id = ?', (session_id,)).fetchone()
        if not row:
            return None
        session = json.loads(row[0])
        session.setdefault('created_at',session['messages'][0]['created_at'])
        session.setdefault('updated_at',session['messages'][-1]['created_at'])
        session.setdefault('artifacts',[])
        session.setdefault('sketches', [])
        session.setdefault('whiteboard', empty_board())
        session['whiteboard'].setdefault('diagrams', [])
        session['whiteboard'].setdefault('last_clear_id', None)
        return session

    def list_sessions(self):
        with self.connect() as db:
            rows=db.execute('SELECT id FROM sessions').fetchall()
        return sorted((self.get(row[0]) for row in rows),key=lambda session:session['updated_at'],reverse=True)

    def save(self, session: dict, snapshot_image: tuple[str,bytes] | None = None):
        now=datetime.now(timezone.utc).isoformat()
        with self.connect() as db:
            old=db.execute('SELECT data FROM sessions WHERE id = ?',(session['id'],)).fetchone()
            previous=json.loads(old[0]) if old else None
            board=session['whiteboard']
            if previous and previous['whiteboard']['revision']!=board['revision']:
                if not previous.get('artifacts') and not session.get('artifacts'):
                    from backend.reports import collect_artifacts
                    recovered=collect_artifacts(previous)
                    for item in recovered:item['description']='Earlier saved board'
                    session.setdefault('artifacts',[]).extend(recovered)
                action=board.get('last_action') or {}
                session.setdefault('artifacts',[]).append({'id':str(uuid4()),'created_at':now,'revision':board['revision'],
                    'source':action.get('source','system'),'source_event_id':action.get('source_event_id'),
                    'description':action.get('description','A new practice board'),'legacy':False,
                    'whiteboard':{'bars':board['bars'],'diagrams':board.get('diagrams',[])}})
            session.setdefault('created_at',session['messages'][0]['created_at'])
            session['updated_at']=now
            if snapshot_image:
                db.execute('INSERT OR IGNORE INTO snapshots VALUES (?, ?)',snapshot_image)
            db.execute('UPDATE sessions SET data = ? WHERE id = ?', (json.dumps(session), session['id']))

    def image_hashes(self):
        with self.connect() as db:
            return {row[0] for row in db.execute('SELECT sha256 FROM snapshots').fetchall()}

    def get_image(self, sha256):
        with self.connect() as db:
            row=db.execute('SELECT png FROM snapshots WHERE sha256 = ?',(sha256,)).fetchone()
        return row[0] if row else None
