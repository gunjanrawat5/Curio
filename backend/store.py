"""Small durable local session store. One atomic write per completed turn."""
import json
import os
import sqlite3
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

GREETING = 'I know a little about fractions… but I get the pieces mixed up. Can you teach me why ⅓ is bigger than ¼?'
CHALLENGE = 'A new puzzle! Draw your own bars to compare 1/6 and 1/8. Which is bigger, and why?'

def event(role: str, text: str, kind: str = 'message') -> dict:
    return {'id': str(uuid4()), 'role': role, 'text': text, 'kind': kind, 'created_at': datetime.now(timezone.utc).isoformat()}

class SessionStore:
    def __init__(self, path: str | None = None):
        self.path = path or os.getenv('CURIO_DB_PATH', str(Path(__file__).parent / 'data' / 'curio.sqlite3'))
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, data TEXT NOT NULL)')

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def create(self) -> dict:
        session = {'id': str(uuid4()), 'topic_id': 'fractions_intro', 'phase': 'teaching', 'messages': [event('curio', GREETING)], 'hints': 0, 'requests': {}}
        with self.connect() as db:
            db.execute('INSERT INTO sessions VALUES (?, ?)', (session['id'], json.dumps(session)))
        return session

    def get(self, session_id: str) -> dict | None:
        with self.connect() as db:
            row = db.execute('SELECT data FROM sessions WHERE id = ?', (session_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def save(self, session: dict):
        with self.connect() as db:
            db.execute('UPDATE sessions SET data = ? WHERE id = ?', (json.dumps(session), session['id']))
