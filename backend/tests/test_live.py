import asyncio
import base64
from types import SimpleNamespace
from fastapi.websockets import WebSocketDisconnect
from google.genai import types
import pytest
from backend import live,main
from backend.tests.test_sessions import client,session,action

class FakeLive:
    def __init__(self,mode='normal'):
        self.queue=asyncio.Queue();self.responses=[];self.mode=mode
    async def send_realtime_input(self,**kwargs):
        if 'audio' in kwargs:
            assert kwargs['audio'].mime_type=='audio/pcm;rate=16000'
            await self.queue.put(types.LiveServerMessage(server_content=types.LiveServerContent(input_transcription=types.Transcription(text='Draw 1/3.'))))
            await self.queue.put(types.LiveServerMessage(tool_call=types.LiveServerToolCall(function_calls=[types.FunctionCall(id='call-1',name='edit_whiteboard',args={'commands':[{'type':'clear_whiteboard'},{'type':'create_fraction_bar','numerator':1,'denominator':3}]})])))
            # Native Live ends the tool-call turn before the spoken follow-up turn.
            await self.queue.put(types.LiveServerMessage(server_content=types.LiveServerContent(turn_complete=True)))
    async def send_tool_response(self,**kwargs):
        self.responses.extend(kwargs['function_responses'])
        await self.queue.put(types.LiveServerMessage(server_content=types.LiveServerContent(output_transcription=types.Transcription(text='Here is the bar.'),model_turn=types.Content(role='model',parts=[types.Part(inline_data=types.Blob(data=b'\x00\x01',mime_type='audio/pcm;rate=24000'))]))))
        if self.mode=='interrupted':await self.queue.put(types.LiveServerMessage(server_content=types.LiveServerContent(interrupted=True)))
        else:await self.queue.put(types.LiveServerMessage(server_content=types.LiveServerContent(turn_complete=True)))
    async def receive(self):
        while True:
            item=await self.queue.get();yield item
            if item.server_content and item.server_content.turn_complete:return

@pytest.fixture
def fake_provider(monkeypatch):
    connections=[]
    class FakeConnection:
        async def __aenter__(self):
            self.fake=FakeLive();connections.append(self.fake);return self.fake
        async def __aexit__(self,*args):pass
    class FakeClient:
        def __init__(self):self.aio=self;self.live=self
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        def connect(self,**kwargs):
            assert kwargs['config'].input_audio_transcription is not None
            assert kwargs['config'].output_audio_transcription is not None
            return FakeConnection()
    monkeypatch.setenv('GEMINI_API_KEY','test-secret')
    monkeypatch.setattr(live.genai,'Client',lambda **kwargs:FakeClient())
    return connections

def connect(client,id):
    return client.websocket_connect('/sessions/'+id+'/voice',headers={'origin':'http://localhost:3000'})

def receive_until(ws,kind):
    items=[]
    for _ in range(20):
        item=ws.receive_json();items.append(item)
        if item['type']==kind:return items
    raise AssertionError(f'Did not receive {kind}')

def test_native_voice_transcripts_tools_and_graceful_stop(client,fake_provider):
    data=session(client)
    with connect(client,data['id']) as ws:
        ws.send_json({'type':'start','sketch_revision':'a'*64})
        assert ws.receive_json()['type']=='ready'
        assert client.post('/sessions/'+data['id']+'/messages',json={**action(),'text':'competing message'}).status_code==409
        ws.send_json({'type':'audio','data':base64.b64encode(b'\x01\x00'*160).decode()})
        events=receive_until(ws,'turn_complete')
        assert any(e['type']=='audio' and e['sample_rate']==24000 for e in events)
        saved=next(e['session'] for e in events if e['type']=='session' and e.get('committed'))
        assert saved['messages'][-2]['text']=='Draw 1/3.'
        assert saved['messages'][-1]['text']=='Here is the bar.'
        assert saved['messages'][-1]['kind']=='voice'
        assert len(saved['whiteboard']['bars'])==1
        assert fake_provider[0].responses[0].response['ok']
        ws.send_json({'type':'stop'})
        assert ws.receive_json()['type']=='ended'
    assert data['id'] not in main.app.state.voice_sessions
    assert client.get('/sessions/'+data['id']).json()==saved

def test_challenge_keeps_voice_but_rejects_drawing_tools(client,fake_provider):
    data=session(client);base='/sessions/'+data['id'];client.post(base+'/challenge',json=action())
    with connect(client,data['id']) as ws:
        ws.send_json({'type':'start'});assert ws.receive_json()['type']=='ready'
        ws.send_json({'type':'audio','data':base64.b64encode(b'\x01\x00').decode()})
        events=receive_until(ws,'turn_complete')
        assert fake_provider[0].responses[0].response['ok'] is False
        assert client.get(base).json()['whiteboard']['bars']==[]
        ws.send_json({'type':'stop'});assert ws.receive_json()['type']=='ended'

def test_voice_checks_origin_session_and_key(client,monkeypatch):
    data=session(client)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect('/sessions/'+data['id']+'/voice',headers={'origin':'https://untrusted.example'}):pass
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    with connect(client,data['id']) as ws:
        assert ws.receive_json()['type']=='error'
    assert data['id'] not in main.app.state.voice_sessions

def test_voice_interruption_saves_actual_partial_transcripts(client,fake_provider):
    data=session(client)
    with connect(client,data['id']) as ws:
        ws.send_json({'type':'start'});assert ws.receive_json()['type']=='ready';fake_provider[0].mode='interrupted'
        ws.send_json({'type':'audio','data':base64.b64encode(b'\x01\x00').decode()})
        events=receive_until(ws,'interrupted')
        saved=ws.receive_json()
        assert saved['type']=='session'
        assert saved['session']['messages'][-1]['kind']=='voice_interrupted'
        ws.send_json({'type':'stop'});assert ws.receive_json()['type']=='ended'

@pytest.mark.parametrize('code,reason,category',[
    (1011,'Resource exhausted.','quota'),
    (1011,'Maximum session duration reached','expired'),
    (1011,'Internal error','provider_unavailable'),
    (1000,'Normal closure','provider_closed'),
    (1008,'Permission denied','configuration'),
    (1006,'Connection lost','network'),
])
def test_close_frame_classification_does_not_blame_configuration_for_every_disconnect(code,reason,category):
    exc=RuntimeError('secret provider payload')
    exc.rcvd=SimpleNamespace(code=code,reason=reason)
    result=live.voice_error_details(exc)
    assert result['category']==category
    assert result['close_code']==code
    assert 'secret' not in result['message']
    if category!='configuration':assert 'account permissions' not in result['message']

def test_app_time_limit_has_a_normal_reconnect_notice(client,fake_provider,monkeypatch):
    monkeypatch.setattr(live,'VOICE_CONNECTION_SECONDS',.01)
    data=session(client)
    with connect(client,data['id']) as ws:
        ws.send_json({'type':'start'})
        assert ws.receive_json()['type']=='ready'
        ended=ws.receive_json()
        assert ended['type']=='ended'
        assert ended['reason']=='time_limit'
        assert 'saved conversation' in ended['message']
        assert 'configuration' not in ended['message']

def test_provider_quota_failure_saves_safe_diagnostics(client,monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','test-secret')
    class FailedConnection:
        async def __aenter__(self):
            exc=RuntimeError('test-secret')
            exc.rcvd=SimpleNamespace(code=1011,reason='Resource exhausted')
            raise exc
        async def __aexit__(self,*args):pass
    class FakeClient:
        def __init__(self):self.aio=self;self.live=self
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        def connect(self,**kwargs):return FailedConnection()
    monkeypatch.setattr(live.genai,'Client',lambda **kwargs:FakeClient())
    data=session(client)
    with connect(client,data['id']) as ws:
        ws.send_json({'type':'start'})
        failure=ws.receive_json()
        assert failure['category']=='quota'
        assert 'test-secret' not in str(failure)
    saved=client.get('/sessions/'+data['id']).json()
    assert saved['voice_disconnects'][-1]['category']=='quota'
    assert saved['voice_disconnects'][-1]['close_code']==1011
    assert 'test-secret' not in str(saved)
