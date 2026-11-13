import base64
from uuid import uuid4
from backend import main
from backend.store import event
from backend.whiteboard import CurioReply
from backend.tests.test_sessions import client,session,action
from backend.tests.test_vision import snapshot,analysis


def test_report_list_search_pagination_and_existing_sessions(client):
    first=session(client);second=session(client)
    stored=main.app.state.store.get(first['id'])
    stored['messages'].extend([event('you','Two equal wholes make a fair comparison.'),event('curio','Why should the pieces be equal?')])
    main.app.state.store.save(stored)
    result=client.get('/reports?limit=1').json()
    assert result['total']==2 and result['has_more']
    assert result['reports'][0]['id']==first['id']
    assert result['reports'][0]['title']=='Two equal wholes make a fair comparison.'
    assert client.get('/reports?limit=1&offset=1').json()['reports'][0]['id']==second['id']
    found=client.get('/reports?q=pieces%20be%20equal').json()
    assert found['total']==1 and found['reports'][0]['id']==first['id']
    assert client.get('/reports?limit=0').status_code==422
    assert client.get('/reports/'+str(uuid4())).status_code==404
    # No provider/evaluator is invoked for either route.
    assert 'requests' not in str(client.get('/reports/'+first['id']).json().keys())


def test_explanation_review_preserves_exact_words_and_assistance_without_grading(client):
    data=session(client);stored=main.app.state.store.get(data['id'])
    hint=event('curio','Think about the same whole.','hint')
    child=event('you','More equal pieces means smaller pieces.','voice')
    follow=event('curio','Why does that happen?','voice')
    challenge=event('curio','Try a new pair.','challenge')
    transfer=event('you','I would compare the same size wholes.')
    stored['messages'].extend([hint,child,follow,challenge,transfer,event('curio','Back to exploring.','explore')])
    main.app.state.store.save(stored)
    report=client.get('/reports/'+data['id']).json()
    assert report['messages']==stored['messages']
    assert report['contributions'][0]['message']==child
    assert report['contributions'][0]['follow_ups'][0]==follow
    assert report['contributions'][0]['prior_hint_ids']==[hint['id']]
    assert report['contributions'][1]['phase']=='independent_practice'
    assert report['result_summary']['practice_status']=='left_practice'
    assert report['result_summary']['status']=='not_assessed'
    assert report['result_summary']['metrics_available'] is False
    assert not any(key in report for key in ('score','mastery','accuracy'))


def test_all_diagram_outputs_survive_clear_and_undo(client):
    data=session(client);base='/sessions/'+data['id']
    create={'type':'create_fraction_bar','numerator':2,'denominator':5}
    client.post(base+'/whiteboard',json={**action(),'operation':'edit','canvas_revision':0,'commands':[create]})
    client.post(base+'/whiteboard',json={**action(),'operation':'clear','canvas_revision':1})
    client.post(base+'/whiteboard',json={**action(),'operation':'undo','canvas_revision':2})
    report=client.get('/reports/'+data['id']).json()
    assert [a['revision'] for a in report['artifacts']]==[1,2,3]
    assert report['artifacts'][0]['whiteboard']['bars'][0]['numerator']==2
    assert report['artifacts'][1]['whiteboard']['bars']==[]
    assert report['artifacts'][2]['whiteboard']['bars'][0]['denominator']==5
    assert 'artifacts' not in client.get(base).json()


def test_new_shared_sketch_is_retained_and_scoped_to_its_report(client,monkeypatch):
    async def inspect(*args):return analysis()
    monkeypatch.setattr(main,'analyze_sketch',inspect)
    data=session(client);other=session(client)
    sent=snapshot()
    response=client.post('/sessions/'+data['id']+'/sketch',json={**action(),'snapshot':sent}).json()
    evidence=response['sketches'][0]
    report=client.get('/reports/'+data['id']).json()
    assert report['sketches'][0]['image_available']
    assert 'png_base64' not in str(report)
    image=client.get(f"/reports/{data['id']}/sketches/{evidence['event_id']}")
    assert image.status_code==200 and image.headers['content-type']=='image/png'
    assert image.content==base64.b64decode(sent['png_base64'])
    assert client.get(f"/reports/{other['id']}/sketches/{evidence['event_id']}").status_code==404


def test_legacy_board_is_recovered_before_new_outputs_are_archived(client):
    import json
    data=session(client)
    # An actual pre-archive session, inserted without using the new store's save hook.
    stored=main.app.state.store.get(data['id']);stored.pop('artifacts',None)
    stored['whiteboard']['revision']=7
    stored['whiteboard']['bars']=[{'id':'old-bar','numerator':1,'denominator':3,'shaded_parts':[0],'source':'ai','source_event_id':'old-event'}]
    stored['sketches']=[{'event_id':str(uuid4()),'created_at':stored['created_at'],'canvas_revision':7,'sketch_revision':'a'*64,'image_sha256':'b'*64,'stroke_count':1,'analysis':analysis().model_dump()}]
    with main.app.state.store.connect() as db:db.execute('UPDATE sessions SET data=? WHERE id=?',(json.dumps(stored),data['id']))
    before=client.get('/reports/'+data['id']).json()
    assert before['archive_note']
    assert before['sketches'][0]['image_available'] is False
    assert before['artifacts'][0]['whiteboard']['bars'][0]['id']=='old-bar'
    client.post('/sessions/'+data['id']+'/whiteboard',json={**action(),'operation':'clear','canvas_revision':7})
    after=client.get('/reports/'+data['id']).json()
    assert after['artifacts'][0]['whiteboard']['bars'][0]['id']=='old-bar'
    assert after['artifacts'][-1]['whiteboard']['bars']==[]


def test_diagram_request_is_linked_to_the_exact_chat_message(client,monkeypatch):
    from backend.whiteboard import CreateBar
    async def reply(*args):return CurioReply(text='Here is a fraction bar.',commands=[CreateBar(type='create_fraction_bar',numerator=1,denominator=3)])
    monkeypatch.setattr(main,'generate_reply',reply)
    data=session(client)
    response=client.post('/sessions/'+data['id']+'/messages',json={**action(),'text':'draw 1/3','canvas_revision':0}).json()
    report=client.get('/reports/'+data['id']).json()
    assert report['artifacts'][0]['source_event_id']==response['messages'][-2]['id']
    assert report['artifacts'][0]['source']=='ai'
