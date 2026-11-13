import asyncio
import base64
import io
from types import SimpleNamespace
from PIL import Image
import pytest
from backend import main, vision
from backend.vision import CanvasSnapshot, SketchAnalysis, Observation, grounded_analysis
from backend.whiteboard import empty_board, CreateBar, CurioReply
from backend.tests.test_sessions import client, session, action


def image_base64(width=800,height=540):
    output=io.BytesIO();Image.new('RGB',(width,height),'white').save(output,format='PNG')
    return base64.b64encode(output.getvalue()).decode()

def snapshot(**overrides):
    return {'png_base64':image_base64(),'canvas_revision':0,'sketch_revision':'a'*64,'stroke_count':1,**overrides}

def analysis(**overrides):
    return SketchAnalysis(summary='A hand-drawn triangle.',observations=[Observation(description='A triangle outline near the middle.',mark='shape',confidence=.9)],needs_clarification=False,reply='I can see a triangle outline. What can you tell me about its sides?',**overrides)

@pytest.mark.parametrize('data',['not base64','<svg/>',base64.b64encode(b'not an image').decode(),image_base64(1601,1)])
def test_invalid_image_rejected(data):
    with pytest.raises(ValueError):CanvasSnapshot(**snapshot(png_base64=data)).decode()

def test_valid_png_and_ambiguous_marks():
    assert CanvasSnapshot(**snapshot()).decode().startswith(b'\x89PNG')
    low=analysis();low.observations[0].confidence=.5
    guarded=grounded_analysis(low,empty_board())
    assert guarded.needs_clarification
    assert 'not sure' in guarded.reply
    assert low.needs_clarification is False
    bad=analysis();bad.observations[0].element_id='invented-id'
    guarded=grounded_analysis(bad,empty_board())
    assert guarded.needs_clarification
    assert guarded.observations[0].element_id is None

def test_part_references_must_be_in_bounds():
    board=empty_board();board['bars']=[{'id':'bar','denominator':3}]
    seen=analysis();seen.observations[0].element_id='bar';seen.observations[0].part_index=3
    assert grounded_analysis(seen,board).needs_clarification
    seen.observations[0].part_index=2
    assert not grounded_analysis(seen,board).needs_clarification

def test_sketch_route_is_idempotent_preserves_drawing_and_never_saves_pixels(client,monkeypatch):
    seen=[]
    async def inspect(image,snapshot,board,messages,phase,question):
        seen.append((image,snapshot,phase,question));return analysis()
    monkeypatch.setattr(main,'analyze_sketch',inspect)
    data=session(client);base='/sessions/'+data['id']
    body={**action(),'snapshot':snapshot(),'question':'What do you see?'}
    result=client.post(base+'/sketch',json=body)
    assert result.status_code==200
    saved=result.json()
    assert seen[0][0].startswith(b'\x89PNG')
    assert saved['whiteboard']==data['whiteboard']
    assert saved['sketches'][0]['canvas_revision']==0
    assert len(saved['sketches'][0]['image_sha256'])==64
    assert saved['messages'][-2]['kind']=='sketch'
    assert saved['messages'][-1]['kind']=='sketch_reply'
    assert 'png_base64' not in str(main.app.state.store.get(data['id']))
    assert client.post(base+'/sketch',json=body).json()==saved
    assert len(seen)==1
    assert client.post(base+'/sketch',json={**body,'question':'changed'}).status_code==409

def test_stale_snapshot_and_bad_data_do_not_call_provider(client,monkeypatch):
    async def inspect(*args):raise AssertionError('Provider should not be called')
    monkeypatch.setattr(main,'analyze_sketch',inspect)
    base='/sessions/'+session(client)['id']
    assert client.post(base+'/sketch',json={**action(),'snapshot':snapshot(canvas_revision=99)}).status_code==409
    assert client.post(base+'/sketch',json={**action(),'snapshot':snapshot(png_base64='bad')}).status_code==422
    assert client.post(base+'/sketch',json={**action(),'snapshot':snapshot(sketch_revision='bad')}).status_code==422

def test_provider_failure_does_not_commit_sketch(client,monkeypatch):
    async def inspect(*args):raise vision.ProviderError('Retry',502)
    monkeypatch.setattr(main,'analyze_sketch',inspect)
    data=session(client);base='/sessions/'+data['id']
    assert client.post(base+'/sketch',json={**action(),'snapshot':snapshot()}).status_code==502
    assert client.get(base).json()==data

def test_challenge_sketch_inspection_is_allowed_without_drawing_changes(client,monkeypatch):
    async def inspect(image,snapshot,board,messages,phase,question):
        assert phase=='challenge'
        return analysis()
    monkeypatch.setattr(main,'analyze_sketch',inspect)
    base='/sessions/'+session(client)['id']
    before=client.post(base+'/challenge',json=action()).json()
    result=client.post(base+'/sketch',json={**action(),'snapshot':snapshot(canvas_revision=1)}).json()
    assert result['phase']=='challenge'
    assert result['whiteboard']==before['whiteboard']
    assert 'mastery' not in result

def test_only_matching_snapshot_context_is_passed_to_chat(client,monkeypatch):
    async def inspect(*args):return analysis()
    monkeypatch.setattr(main,'analyze_sketch',inspect)
    contexts=[]
    async def reply(messages,phase,board):
        contexts.append(board);return CurioReply(text='Tell me more.')
    monkeypatch.setattr(main,'generate_reply',reply)
    base='/sessions/'+session(client)['id']
    client.post(base+'/sketch',json={**action(),'snapshot':snapshot()})
    for stroke_revision in ['a'*64,'b'*64,None]:
        payload={**action(),'text':'What did I draw?','canvas_revision':0,'sketch_revision':stroke_revision}
        assert client.post(base+'/messages',json=payload).status_code==200
    assert contexts[0]['vision_context']['current']
    assert 'vision_context' not in contexts[1]
    assert 'vision_context' not in contexts[2]
    client.post(base+'/whiteboard',json={**action(),'operation':'clear','canvas_revision':0})
    client.post(base+'/messages',json={**action(),'text':'What did I draw?','canvas_revision':1,'sketch_revision':'a'*64})
    assert 'vision_context' not in contexts[-1]

def test_sdk_receives_image_bytes_and_structured_uncertainty_schema(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','test-secret')
    calls=[]
    class FakeClient:
        def __init__(self):self.models=self
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def generate_content(self,**kwargs):calls.append(kwargs);return SimpleNamespace(text=analysis().model_dump_json())
    monkeypatch.setattr(vision.genai,'Client',lambda **kwargs:SimpleNamespace(aio=FakeClient()))
    data=CanvasSnapshot(**snapshot());image=data.decode()
    result=asyncio.run(vision.analyze_sketch(image,data,empty_board(),[],'teaching','What do you see?'))
    assert result.observations[0].mark=='shape'
    parts=calls[0]['contents'][0].parts
    assert parts[1].inline_data.mime_type=='image/png'
    assert parts[1].inline_data.data==image
    assert 'needs_clarification' in calls[0]['config'].response_json_schema['properties']
