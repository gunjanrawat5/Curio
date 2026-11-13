import math
import pytest
from pydantic import ValidationError
from backend.diagrams import MathElement, CreateDiagram, CreateGraph, MoveElement, EditLabel, parse_expression, evaluate, sample_graph
from backend.whiteboard import empty_board, apply_commands, BoardError, CreateBar
from backend.tests.test_sessions import client, session, action

def triangle():
    return CreateDiagram(type='create_math_diagram',title='A triangle',elements=[MathElement(kind='polygon',points=[{'x':100,'y':300},{'x':400,'y':300},{'x':100,'y':100}]),MathElement(kind='text',x=100,y=330,text='A')])

def test_geometry_editing_keeps_ids_and_history():
    board=apply_commands(empty_board(),[triangle()],'ai','event-1','teaching')
    label=board['diagrams'][0]['elements'][1]
    moved=apply_commands(board,[MoveElement(type='move_math_element',element_id=label['id'],dx=10,dy=-10),EditLabel(type='edit_math_label',element_id=label['id'],text='B')],'learner','event-2','teaching')
    changed=moved['diagrams'][0]['elements'][1]
    assert changed['id']==label['id']
    assert (changed['x'],changed['y'],changed['text'])==(110,320,'B')
    assert moved['history'][-1]['diagrams']==board['diagrams']
    assert board['diagrams'][0]['elements'][1]['text']=='A'

@pytest.mark.parametrize('element',[
    {'kind':'circle','x':10,'y':10,'radius':30},
    {'kind':'polygon','points':[{'x':0,'y':0}]},
    {'kind':'text','text':''},
    {'kind':'line','x':math.nan},
    {'kind':'line','x2':701},
    {'kind':'image','text':'https://example.com'},
])
def test_invalid_geometry_rejected(element):
    with pytest.raises(ValidationError):MathElement.model_validate(element)

def test_graph_values_are_computed_and_discontinuities_split():
    graph=CreateGraph(type='create_function_graph',expression='x^2',x_min=-2,x_max=2,y_min=0,y_max=4)
    points=sample_graph(graph)[0]
    assert points[0]=={'x':50,'y':50}
    assert points[200]=={'x':350,'y':350}
    assert points[-1]=={'x':650,'y':50}
    reciprocal=CreateGraph(type='create_function_graph',expression='1/x')
    segments=sample_graph(reciprocal)
    assert len(segments)>=2
    assert all(not (segment[0]['x']<350<segment[-1]['x']) for segment in segments)
    assert evaluate(parse_expression('sin(pi/2)+sqrt(4)'),0)==3

@pytest.mark.parametrize('expression', ["__import__('os')",'x.__class__','[x for x in range(10)]','2**1000000','x**x','open(1)','sin(x,2)','True','1e999','lambda:1'])
def test_expression_allowlist(expression):
    with pytest.raises((ValueError,SyntaxError)):parse_expression(expression)

def test_graph_ranges_and_occupancy():
    with pytest.raises(ValidationError):CreateGraph(type='create_function_graph',expression='x',x_min=4,x_max=1)
    with pytest.raises(ValueError):sample_graph(CreateGraph(type='create_function_graph',expression='100000'))
    board=apply_commands(empty_board(),[triangle()],'ai','event','teaching')
    with pytest.raises(BoardError):apply_commands(board,[triangle()],'ai','event','teaching')
    with pytest.raises(BoardError):apply_commands(board,[CreateBar(type='create_fraction_bar',numerator=1,denominator=3)],'ai','event','teaching')
    with pytest.raises(BoardError):apply_commands(empty_board(),[triangle()],'ai','event','challenge')
    with pytest.raises(BoardError):apply_commands(board,[MoveElement(type='move_math_element',element_id=board['diagrams'][0]['elements'][1]['id'],dx=700,dy=0)],'learner','event','teaching')

def test_diagram_clear_and_undo_api(client):
    base='/sessions/'+session(client)['id']
    draw=client.post(base+'/whiteboard',json={**action(),'operation':'edit','canvas_revision':0,'commands':[triangle().model_dump()]}).json()
    assert len(draw['whiteboard']['diagrams'])==1
    cleared=client.post(base+'/whiteboard',json={**action(),'operation':'clear','canvas_revision':1}).json()
    assert cleared['whiteboard']['diagrams']==[]
    undone=client.post(base+'/whiteboard',json={**action(),'operation':'undo','canvas_revision':2}).json()
    assert undone['whiteboard']['diagrams']==draw['whiteboard']['diagrams']

def test_provider_schema_retains_required_fields_without_multiplying_size_limits():
    from backend.whiteboard import provider_reply_schema
    schema=provider_reply_schema()
    diagram=schema['$defs']['CreateDiagram']
    assert 'title' in diagram['properties']
    assert {'type','title','elements'}.issubset(set(diagram['required']))
    assert 'maxItems' not in diagram['properties']['elements']
    # The actual local validator still rejects oversized diagrams.
    with pytest.raises(ValidationError):
        CreateDiagram(type='create_math_diagram',title='too many',elements=[MathElement(kind='line') for _ in range(61)])
