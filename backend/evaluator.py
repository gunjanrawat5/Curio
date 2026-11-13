"""One-shot rubric evaluation with learner-only, quote-checked evidence."""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types
from backend.gemini import ProviderError

ROOT = Path(__file__).parent / 'evaluation'
RUBRIC = json.loads((ROOT / 'rubric.json').read_text())
SHOWN = {'demonstrated_independent', 'demonstrated_assisted'}


def transcript(session):
    events = []
    sketches = {s['event_id']: s for s in session.get('sketches', [])}
    for m in session['messages']:
        kind = m.get('kind', '')
        text = m['text']
        if m['role'] == 'you' and kind == 'sketch':
            sketch = sketches.get(m['id'])
            if sketch and not sketch['analysis'].get('needs_clarification'):
                text += '\nSketch observation: ' + sketch['analysis']['summary']
        events.append({'id': m['id'], 'actor': 'learner' if m['role'] == 'you' else 'pip',
                       'modality': 'sketch' if kind == 'sketch' else 'voice' if kind.startswith('voice') else 'text', 'text': text})
    return {'session_id': session['id'], 'topic_id': RUBRIC['topic_id'], 'learner_name': 'Learner',
            'started_at': session['created_at'], 'ended_at': session['messages'][-1]['created_at'],
            'events': events, 'hints': [m for m in session['messages'] if m.get('kind') == 'hint'], 'transfer': None}


def normalize(s):
    return re.sub(r'\s+', ' ', s.lower().translate(str.maketrans({'’': "'", '‘': "'", '“': '"', '”': '"'}))).strip()


def validate_report(raw, log):
    learners = {e['id']: e['text'] for e in log['events'] if e['actor'] == 'learner'}
    order = {e['id']: i for i, e in enumerate(log['events'])}
    def quote(value, event_id):
        return value if isinstance(value, str) and normalize(value) and event_id in learners and normalize(value) in normalize(learners[event_id]) else None
    def items(name):
        return {o.get('id'): o for o in (raw.get(name) if isinstance(raw.get(name), list) else []) if isinstance(o, dict)}
    objectives = []
    for rule in RUBRIC['objectives']:
        o = items('objectives').get(rule['id'], {})
        q = quote(o.get('quote'), o.get('quote_event_id'))
        before = o.get('before') if o.get('before') in RUBRIC['statuses'] else 'not_observed'
        after = o.get('after') if o.get('after') in RUBRIC['statuses'] else 'not_observed'
        if not q:
            if before in SHOWN: before = 'not_observed'
            if after in SHOWN: after = 'not_observed'
        objectives.append({'id': rule['id'], 'label': rule['label'], 'before': before, 'after': after,
                           'quote': q, 'quote_event_id': o.get('quote_event_id') if q else None, 'note': str(o.get('note') or '')})
    misconceptions = []
    for rule in RUBRIC['misconceptions']:
        m = items('misconceptions').get(rule['id'], {})
        q = quote(m.get('quote'), m.get('quote_event_id'))
        if not q: continue
        resolution = quote(m.get('resolution_quote'), m.get('resolution_event_id'))
        resolved = m.get('resolved') is True and bool(resolution) and order.get(m.get('resolution_event_id'), -1) > order.get(m.get('quote_event_id'), -1)
        misconceptions.append({'id': rule['id'], 'label': rule['label'], 'quote': q, 'quote_event_id': m['quote_event_id'],
                               'how_detected': str(m.get('how_detected') or ''), 'resolved': resolved,
                               'resolution_quote': resolution if resolved else None, 'resolution_event_id': m.get('resolution_event_id') if resolved else None})
    # The current demo has no independent transfer task; model claims cannot create one.
    outcome = 'more_evidence_needed' if sum(o['after'] == 'not_observed' for o in objectives) > len(objectives) / 2 else 'developing'
    duration = max(0, int((datetime.fromisoformat(log['ended_at']) - datetime.fromisoformat(log['started_at'])).total_seconds()))
    return {'sample': False, 'session': {'learner_name': log['learner_name'], 'topic': RUBRIC['title'], 'date': log['started_at'][:10], 'duration_seconds': duration, 'hint_count': len(log['hints'])},
            'outcome': outcome, 'summary': str(raw.get('summary') or ''), 'objectives': objectives, 'misconceptions': misconceptions,
            'transfer': {'attempted': False, 'passed': None, 'task': None, 'quote': None},
            'next_steps': [s for s in (raw.get('next_steps') if isinstance(raw.get('next_steps'), list) else []) if isinstance(s, str)][:5]}


async def evaluate(session):
    key = os.getenv('GEMINI_API_KEY', '').strip()
    if not key: raise ProviderError('Add GEMINI_API_KEY to evaluate this conversation.', 503)
    log = transcript(session)
    prompt = (ROOT / 'evaluator_prompt.md').read_text().replace('{rubric}', json.dumps(RUBRIC)).replace('{transcript}', json.dumps(log))
    try:
        async with genai.Client(api_key=key, http_options=types.HttpOptions(timeout=30000)).aio as client:
            for attempt in range(2):
                response = await client.models.generate_content(model=os.getenv('GEMINI_EVALUATION_MODEL') or os.getenv('GEMINI_MODEL', 'gemini-3.8-flash'), contents=prompt,
                    config=types.GenerateContentConfig(temperature=0, response_mime_type='application/json', max_output_tokens=4096))
                try:
                    raw = json.loads(response.text or '')
                    if not isinstance(raw, dict): raise ValueError()
                    return validate_report(raw, log)
                except (ValueError, TypeError):
                    if attempt: raise ProviderError('The evaluation response was invalid. Please retry.')
    except ProviderError: raise
    except Exception: raise ProviderError('Evaluation could not reach Gemini. Check the backend model and key, then retry.') from None
