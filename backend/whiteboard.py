"""Allowlisted diagram commands; geometry, ownership and revisions are app-owned."""
from copy import deepcopy
from collections import Counter
import re
from typing import Literal
from uuid import uuid4
from backend.diagrams import CreateDiagram, CreateGraph, MoveElement, EditLabel, MathElement, sample_graph
from pydantic import BaseModel, ConfigDict, Field, model_validator

class CreateBar(BaseModel):
    model_config = ConfigDict(extra='forbid')
    type: Literal['create_fraction_bar']
    numerator: int = Field(ge=0, le=24, strict=True)
    denominator: int = Field(ge=1, le=24, strict=True)

    @model_validator(mode='after')
    def valid_fraction(self):
        if self.numerator > self.denominator:
            raise ValueError('The numerator must not exceed the denominator.')
        return self

class ShadePart(BaseModel):
    model_config = ConfigDict(extra='forbid')
    type: Literal['shade_fraction_part']
    bar_id: str = Field(min_length=1, max_length=80)
    part_index: int = Field(ge=0, le=23, strict=True)
    shaded: bool

class ClearBoard(BaseModel):
    model_config = ConfigDict(extra='forbid')
    type: Literal['clear_whiteboard']
    clear_freehand: bool = True

DiagramCommand = ClearBoard | CreateBar | ShadePart | CreateDiagram | CreateGraph | MoveElement | EditLabel

class CurioReply(BaseModel):
    model_config = ConfigDict(extra='forbid')
    text: str = Field(min_length=1, max_length=4000)
    commands: list[DiagramCommand] = Field(default_factory=list, max_length=8)

class BoardError(ValueError):
    pass

def empty_board():
    return {'revision': 0, 'bars': [], 'diagrams': [], 'history': [], 'last_action': None, 'last_clear_id': None}

def apply_commands(board: dict, commands: list, source: str, source_event_id: str, phase: str, request_text: str = "") -> dict:
    if not commands:
        return deepcopy(board)
    if phase == 'challenge':
        raise BoardError('Curio cannot draw or shade during independent practice. Use the pen to draw your own bars.')
    requested = [(int(a), int(b)) for a, b in re.findall(r'(?<![\d.])(-?\d+)\s*/\s*(-?\d+)(?!\d|\.\d)', request_text)]
    created = [(c.numerator, c.denominator) for c in commands if isinstance(c, CreateBar)]
    if created and requested and Counter(created) != Counter(requested):
        raise BoardError('I could not match that drawing to your exact fractions. Please ask for the bars again using fractions like 2/3 and 2/5.')
    result = deepcopy(board)
    for command in commands:
        if isinstance(command, ClearBoard):
            result['bars'] = []
            result['diagrams'] = []
            if command.clear_freehand:
                result['last_clear_id'] = str(uuid4())
        elif isinstance(command, CreateBar):
            if result.get('diagrams'):
                raise BoardError('Please clear the current diagram before adding fraction bars.')
            if len(result['bars']) >= 4:
                raise BoardError('There is room for four bars. Undo or clear the bars before adding more.')
            result['bars'].append({'id': str(uuid4()), 'numerator': command.numerator, 'denominator': command.denominator,
                'shaded_parts': list(range(command.numerator)), 'source': source, 'source_event_id': source_event_id})
        elif isinstance(command, ShadePart):
            bar = next((b for b in result['bars'] if b['id'] == command.bar_id), None)
            if bar is None or command.part_index >= bar['denominator']:
                raise BoardError('That piece is no longer on the board. Please try again.')
            parts = set(bar['shaded_parts'])
            if command.shaded:
                parts.add(command.part_index)
            else:
                parts.discard(command.part_index)
            bar['shaded_parts'] = sorted(parts)
        elif isinstance(command, (CreateDiagram, CreateGraph)):
            if result['bars'] or result.get('diagrams'):
                raise BoardError('Please clear the current diagram before drawing a new one. Your pen strokes will stay until you clear them.')
            diagram = {'id': str(uuid4()), 'source': source, 'source_event_id': source_event_id}
            if isinstance(command, CreateDiagram):
                diagram.update({'kind': 'geometry', 'title': command.title, 'elements': [{**item.model_dump(), 'id': str(uuid4())} for item in command.elements]})
            else:
                try:
                    segments = sample_graph(command)
                except (ValueError, SyntaxError, RecursionError) as exc:
                    raise BoardError('I could not plot that expression. Use x, numbers, arithmetic and sin/cos/tan/sqrt/abs/log/exp, with a visible graph range.') from None
                diagram.update({'kind': 'graph', 'title': 'y = ' + command.expression, 'graph': command.model_dump(), 'segments': segments})
            result['diagrams'] = [diagram]
        elif isinstance(command, (MoveElement, EditLabel)):
            diagram = next((d for d in result.get('diagrams', []) if d['kind'] == 'geometry' and any(e['id'] == command.element_id for e in d['elements'])), None)
            if diagram is None:
                raise BoardError('That element is no longer on the board.')
            element = next(e for e in diagram['elements'] if e['id'] == command.element_id)
            changed = {k: v for k, v in element.items() if k != 'id'}
            if isinstance(command, EditLabel):
                if element['kind'] != 'text':
                    raise BoardError('Select a text label to edit it.')
                changed['text'] = command.text
            else:
                if element['kind'] == 'polygon':
                    changed['points'] = [{'x': p['x'] + command.dx, 'y': p['y'] + command.dy} for p in changed['points']]
                else:
                    changed['x'] += command.dx; changed['y'] += command.dy
                    if element['kind'] in ('line', 'arrow'):
                        changed['x2'] += command.dx; changed['y2'] += command.dy
            try:
                validated = MathElement.model_validate(changed)
            except ValueError:
                raise BoardError('Keep the element inside the drawing area.') from None
            element.update(validated.model_dump())
        else:
            raise BoardError('Unsupported drawing action.')

    result['history'].append({'bars': deepcopy(board['bars']), 'diagrams': deepcopy(board.get('diagrams', [])), 'source': source, 'source_event_id': source_event_id,
        'last_clear_id': board.get('last_clear_id'), 'commands': [c.model_dump() for c in commands]})
    result['revision'] += 1
    actor = 'Curio' if source == 'ai' else 'You'
    count = len(created)
    description = f"{actor} drew {count} fraction {'bar' if count == 1 else 'bars'}" if count else f'{actor} edited the shading'
    if any(isinstance(c, (CreateDiagram, CreateGraph)) for c in commands): description = f'{actor} drew a math diagram'
    elif any(isinstance(c, (MoveElement, EditLabel)) for c in commands): description = f'{actor} edited the diagram'
    if any(isinstance(c, ClearBoard) for c in commands):
        description = f'{actor} cleared the board' + (' and drew a new diagram' if any(isinstance(c, (CreateBar, CreateDiagram, CreateGraph)) for c in commands) else '')
    result['last_action'] = {'source': source, 'description': description}
    return result


def provider_reply_schema():
    """Omit size bounds from the provider grammar; validate them in Pydantic.

    Nested maxItems bounds multiply provider grammar states. Keep command-specific
    required fields and alternatives, while enforcing all limits after generation.
    """
    def simplify(schema):
        if isinstance(schema, list): return [simplify(item) for item in schema]
        if not isinstance(schema, dict): return schema
        result = {}
        for key, value in schema.items():
            if key in ('title', 'default', 'minimum', 'maximum', 'minLength', 'maxLength', 'minItems', 'maxItems'):
                continue
            if key in ('properties', '$defs'):
                result[key] = {name: simplify(definition) for name, definition in value.items()}
            else:
                result[key] = simplify(value)
        return result
    return simplify(CurioReply.model_json_schema())
