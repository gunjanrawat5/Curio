from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import main, gemini
from backend.store import SessionStore
from backend.whiteboard import CurioReply

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('CURIO_DB_PATH', str(tmp_path / 'sessions.sqlite3'))
    with TestClient(app) as client:
        yield client

def session(client):
    response = client.post('/sessions')
    assert response.status_code == 201
    return response.json()

def action():
    return {'request_id': str(uuid4())}

def test_persisted_session_and_no_internal_fields(client):
    data = session(client)
    assert 'requests' not in data
    assert data['messages'][0]['role'] == 'curio'
    assert SessionStore().get(data['id'])['messages'] == data['messages']
    assert client.get('/sessions/' + data['id']).json() == data

def test_history_and_retry_are_server_authoritative(client, monkeypatch):
    calls = []
    async def reply(messages, phase, board):
        calls.append((messages, phase))
        return CurioReply(text='Why do the wholes need to be the same size?')
    monkeypatch.setattr(main, 'generate_reply', reply)
    data = session(client)
    path = f"/sessions/{data['id']}/messages"
    body = {**action(), 'text': 'The wholes must be the same size.'}
    result = client.post(path, json=body)
    assert result.status_code == 200
    assert len(result.json()['messages']) == 3
    assert calls[0][0][-1]['text'] == body['text']
    assert calls[0][0][0]['id'] == data['messages'][0]['id']
    assert client.post(path, json=body).json() == result.json()
    assert len(calls) == 1
    assert client.post(path, json={**body, 'text': 'different'}).status_code == 409
    assert client.get('/sessions/' + data['id']).json() == result.json()

def test_provider_failure_does_not_commit_partial_turn(client, monkeypatch):
    async def fail(*args):
        raise gemini.ProviderError('Please retry.', 502)
    monkeypatch.setattr(main, 'generate_reply', fail)
    data = session(client)
    response = client.post(f"/sessions/{data['id']}/messages", json={**action(), 'text': 'my answer'})
    assert response.status_code == 502
    assert client.get('/sessions/' + data['id']).json() == data

def test_hints_and_challenge_preserve_history(client):
    data = session(client)
    base = '/sessions/' + data['id']
    body = action()
    hint = client.post(base + '/hints', json=body).json()
    assert hint['hints'] == 1
    assert hint['messages'][-1]['kind'] == 'hint'
    assert client.post(base + '/hints', json=body).json() == hint
    challenge = client.post(base + '/challenge', json=action()).json()
    assert challenge['phase'] == 'challenge'
    assert len(challenge['messages']) == 3
    assert client.post(base + '/hints', json=action()).status_code == 409

def test_validation_and_unknown_session(client):
    data = session(client)
    for text in ['', '   ', 'x' * 4001]:
        assert client.post(f"/sessions/{data['id']}/messages", json={**action(), 'text': text}).status_code == 422
    assert client.get('/sessions/' + str(uuid4())).status_code == 404
    assert client.get('/sessions/not-a-uuid').status_code == 422

def test_missing_key_is_clear_and_does_not_expose_secrets(client, monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    assert client.get('/health').json()['provider_configured'] is False
    data = session(client)
    result = client.post(f"/sessions/{data['id']}/messages", json={**action(), 'text': 'One third is bigger.'})
    assert result.status_code == 503
    assert 'GEMINI_API_KEY' in result.json()['detail']

def test_cors_allows_browser_posts(client):
    response = client.options('/sessions', headers={'Origin': 'http://localhost:3000', 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'content-type'})
    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == 'http://localhost:3000'

def test_concurrent_duplicate_turn_only_calls_provider_once(client, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    import asyncio
    calls = []
    async def reply(messages, phase, board):
        calls.append(messages)
        await asyncio.sleep(0.03)
        return CurioReply(text='What happens to the pieces?')
    monkeypatch.setattr(main, 'generate_reply', reply)
    data = session(client)
    path = f"/sessions/{data['id']}/messages"
    body = {**action(), 'text': 'We use the same whole.'}
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: client.post(path, json=body), range(2)))
    assert all(response.status_code == 200 for response in responses)
    assert len(calls) == 1
    assert len(client.get('/sessions/' + data['id']).json()['messages']) == 3

def test_exit_challenge_restores_drawing_preserves_history_and_is_idempotent(client, monkeypatch):
    from backend.whiteboard import CreateBar
    data=session(client)
    base='/sessions/'+data['id']
    client.post(base+'/challenge',json=action())
    body=action()
    resumed=client.post(base+'/explore',json=body)
    assert resumed.status_code==200
    state=resumed.json()
    assert state['phase']=='teaching'
    assert [m['kind'] for m in state['messages']]==['message','challenge','explore']
    assert client.post(base+'/explore',json=body).json()==state
    assert client.get(base).json()==state
    async def reply(messages,phase,board):
        assert phase=='teaching'
        return CurioReply(text='Here is a bar.',commands=[CreateBar(type='create_fraction_bar',numerator=1,denominator=3)])
    monkeypatch.setattr(main,'generate_reply',reply)
    drawn=client.post(base+'/messages',json={**action(),'text':'draw 1/3','canvas_revision':state['whiteboard']['revision']}).json()
    assert len(drawn['whiteboard']['bars'])==1
    assert client.post(base+'/hints',json=action()).status_code==200
    again=client.post(base+'/challenge',json=action()).json()
    assert again['phase']=='challenge'
    assert again['whiteboard']['bars']==[]
