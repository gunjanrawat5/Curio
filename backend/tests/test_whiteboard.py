from copy import deepcopy
from uuid import uuid4
import pytest
from pydantic import ValidationError
from backend.whiteboard import CreateBar, ShadePart, CurioReply, BoardError, apply_commands, empty_board
from backend import main
from backend.tests.test_sessions import client, session, action


def create(n=1, d=3):
    return CreateBar(type='create_fraction_bar', numerator=n, denominator=d)

@pytest.mark.parametrize('n,d', [(1,0),(1,25),(-1,3),(4,3),(1,1.5),(True,3)])
def test_invalid_fraction_commands(n,d):
    with pytest.raises(ValidationError):
        create(n,d)

def test_bar_ids_geometry_provenance_and_exact_requested_fractions():
    board = empty_board()
    result = apply_commands(board, [create(2,3), create(2,5)], 'ai', 'event-1', 'teaching', 'draw 2/3 and 2/5.')
    assert board == empty_board()
    assert result['revision'] == 1
    assert len({b['id'] for b in result['bars']}) == 2
    assert result['bars'][0]['shaded_parts'] == [0,1]
    assert result['bars'][1]['source_event_id'] == 'event-1'
    assert all('width' not in bar for bar in result['bars']) # equal-width geometry belongs to renderer
    with pytest.raises(BoardError):
        apply_commands(board, [create(1,3),create(1,4)], 'ai', 'event-1', 'teaching', 'draw 2/3 and 2/5.')

def test_batch_is_atomic_and_stable_bar_ids_allow_shading():
    board = apply_commands(empty_board(), [create()], 'ai', 'event-1', 'teaching')
    original = deepcopy(board)
    command = ShadePart(type='shade_fraction_part', bar_id=board['bars'][0]['id'], part_index=2, shaded=True)
    result = apply_commands(board, [command], 'learner', 'event-2', 'teaching')
    assert result['bars'][0]['shaded_parts'] == [0,2]
    assert result['bars'][0]['id'] == board['bars'][0]['id']
    bad = command.model_copy(update={'part_index': 8})
    with pytest.raises(BoardError):
        apply_commands(board, [create(),bad], 'ai','event-3','teaching')
    assert board == original
    with pytest.raises(BoardError):
        apply_commands(board,[command.model_copy(update={'bar_id':'unknown'})],'ai','event-4','teaching')

def test_no_arbitrary_code_or_unsupported_commands():
    with pytest.raises(ValidationError):
        CurioReply.model_validate({'text':'okay','commands':[{'type':'execute','code':'alert(1)'}]})
    with pytest.raises(ValidationError):
        CurioReply.model_validate({'text':'okay','commands':[{'type':'create_fraction_bar','numerator':1,'denominator':3,'width':200}]})

def test_capacity_and_challenge_protection():
    with pytest.raises(BoardError):
        apply_commands(empty_board(), [create() for _ in range(5)], 'ai', 'event', 'teaching')
    with pytest.raises(BoardError):
        apply_commands(empty_board(), [create()], 'ai', 'event', 'challenge')

def test_ai_actions_retry_persist_shade_undo_and_stale_revision(client, monkeypatch):
    async def reply(messages, phase, board):
        return CurioReply(text='Here are illustrative thirds and fourths.', commands=[create(1,3),create(1,4)])
    monkeypatch.setattr(main,'generate_reply',reply)
    data = session(client)
    base = '/sessions/' + data['id']
    body = {**action(),'text':'draw thirds and fourths','canvas_revision':0}
    result = client.post(base+'/messages',json=body)
    assert result.status_code == 200
    board = result.json()['whiteboard']
    assert [b['denominator'] for b in board['bars']] == [3,4]
    assert board['last_action']['description'] == 'Curio drew 2 fraction bars'
    assert client.post(base+'/messages',json=body).json() == result.json()
    assert client.get(base).json()['whiteboard'] == board
    shade = {**action(),'operation':'edit','canvas_revision':1,'commands':[{'type':'shade_fraction_part','bar_id':board['bars'][0]['id'],'part_index':1,'shaded':True}]}
    edited = client.post(base+'/whiteboard',json=shade).json()['whiteboard']
    assert edited['bars'][0]['shaded_parts'] == [0,1]
    assert client.post(base+'/whiteboard',json=shade).json()['whiteboard'] == edited
    assert client.post(base+'/whiteboard',json={**shade,**action()}).status_code == 409
    undone = client.post(base+'/whiteboard',json={**action(),'operation':'undo','canvas_revision':2}).json()['whiteboard']
    assert undone['bars'] == board['bars']
    restored_empty = client.post(base+'/whiteboard',json={**action(),'operation':'undo','canvas_revision':3}).json()['whiteboard']
    assert restored_empty['bars'] == []
    assert not restored_empty['can_undo']

def test_rejected_ai_commands_do_not_claim_success(client,monkeypatch):
    async def reply(messages,phase,board):
        return CurioReply(text='I drew them!',commands=[create()])
    monkeypatch.setattr(main,'generate_reply',reply)
    data=session(client);base='/sessions/'+data['id']
    for revision,text in [(99,'draw thirds'),(0,'draw 2/5')]:
        result=client.post(base+'/messages',json={**action(),'text':text,'canvas_revision':revision}).json()
        assert result['whiteboard']['bars']==[]
        assert result['messages'][-1]['text']!='I drew them!'
    client.post(base+'/challenge',json=action())
    result=client.post(base+'/messages',json={**action(),'text':'draw thirds','canvas_revision':1}).json()
    assert result['whiteboard']['bars']==[]
    assert 'independent practice' in result['messages'][-1]['text']
    assert client.post(base+'/whiteboard',json={**action(),'operation':'edit','canvas_revision':1,'commands':[create().model_dump()]}).status_code==422

def test_clear_then_draw_is_atomic_and_undo_restores_previous_board(client, monkeypatch):
    from backend.whiteboard import ClearBoard
    original=apply_commands(empty_board(),[create(1,3)],'ai','first','teaching')
    replaced=apply_commands(original,[ClearBoard(type='clear_whiteboard'),create(2,5)],'ai','next','teaching','clear and draw 2/5')
    assert len(replaced['bars'])==1
    assert replaced['bars'][0]['denominator']==5
    assert replaced['last_clear_id']
    assert replaced['history'][-1]['bars']==original['bars']
    assert original['last_clear_id'] is None
    # Failure after clear must leave the existing board untouched.
    with pytest.raises(BoardError):
        apply_commands(original,[ClearBoard(type='clear_whiteboard'),ShadePart(type='shade_fraction_part',bar_id='missing',part_index=0,shaded=True)],'ai','bad','teaching')
    assert len(original['bars'])==1
    with pytest.raises(BoardError):
        apply_commands(original,[ClearBoard(type='clear_whiteboard')],'ai','bad','challenge')
    data=session(client);base='/sessions/'+data['id']
    async def reply(messages,phase,board):
        return CurioReply(text='Cleared and drew the new bars.',commands=[ClearBoard(type='clear_whiteboard'),create(2,5)])
    monkeypatch.setattr(main,'generate_reply',reply)
    body={**action(),'text':'clear and draw 2/5','canvas_revision':0}
    result=client.post(base+'/messages',json=body).json()
    assert result['whiteboard']['last_clear_id']
    assert client.post(base+'/messages',json=body).json()==result
    undone=client.post(base+'/whiteboard',json={**action(),'operation':'undo','canvas_revision':1}).json()
    assert undone['whiteboard']['bars']==[]
    assert undone['whiteboard']['last_clear_id'] is None
    assert undone['whiteboard']['last_action']['operation']=='undo'

def test_clear_without_erasing_freehand_keeps_clear_id():
    from backend.whiteboard import ClearBoard
    board=apply_commands(empty_board(),[ClearBoard(type='clear_whiteboard',clear_freehand=False)],'ai','event','teaching')
    assert board['last_clear_id'] is None
