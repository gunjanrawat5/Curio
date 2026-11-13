"""Bounded math primitives and function sampling without executing model code."""
import ast
import math
import operator
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Point(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    x: float = Field(ge=0, le=700)
    y: float = Field(ge=0, le=400)

class MathElement(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    kind: Literal['line', 'arrow', 'circle', 'polygon', 'text']
    x: float = Field(default=0, ge=0, le=700)
    y: float = Field(default=0, ge=0, le=400)
    x2: float = Field(default=0, ge=0, le=700)
    y2: float = Field(default=0, ge=0, le=400)
    radius: float = Field(default=0, ge=0, le=190)
    points: list[Point] = Field(default_factory=list, max_length=32)
    text: str = Field(default='', max_length=120)
    color: Literal['purple', 'orange', 'green', 'ink'] = 'purple'
    filled: bool = False

    @model_validator(mode='after')
    def geometry(self):
        if self.kind == 'circle' and (self.radius <= 0 or self.x-self.radius < 0 or self.x+self.radius > 700 or self.y-self.radius < 0 or self.y+self.radius > 400):
            raise ValueError('Circle must fit inside the drawing.')
        if self.kind == 'polygon' and len(self.points) < 3:
            raise ValueError('Polygons need at least three points.')
        if self.kind == 'text' and not self.text.strip():
            raise ValueError('A label needs text.')
        return self

class CreateDiagram(BaseModel):
    model_config = ConfigDict(extra='forbid')
    type: Literal['create_math_diagram']
    title: str = Field(min_length=1, max_length=80)
    elements: list[MathElement] = Field(min_length=1, max_length=60)

class CreateGraph(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    type: Literal['create_function_graph']
    expression: str = Field(min_length=1, max_length=120)
    x_min: float = Field(default=-5, ge=-100, le=100)
    x_max: float = Field(default=5, ge=-100, le=100)
    y_min: float = Field(default=-5, ge=-1000, le=1000)
    y_max: float = Field(default=5, ge=-1000, le=1000)

    @model_validator(mode='after')
    def valid_ranges(self):
        if self.x_max-self.x_min < .1 or self.y_max-self.y_min < .1:
            raise ValueError('Graph ranges must be increasing and at least 0.1 wide.')
        return self

class MoveElement(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    type: Literal['move_math_element']
    element_id: str = Field(min_length=1, max_length=80)
    dx: float = Field(ge=-700, le=700)
    dy: float = Field(ge=-400, le=400)

class EditLabel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    type: Literal['edit_math_label']
    element_id: str = Field(min_length=1, max_length=80)
    text: str = Field(min_length=1, max_length=120)

_FUNCTIONS = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'sqrt': math.sqrt, 'abs': abs, 'log': math.log, 'exp': math.exp}
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow}

def parse_expression(expression):
    expression = expression.strip()
    if expression.startswith('y=') or expression.startswith('y ='):
        expression = expression.split('=', 1)[1].strip()
    tree = ast.parse(expression.replace('^', '**'), mode='eval')
    if len(list(ast.walk(tree))) > 60:
        raise ValueError('Expression is too complex.')
    def validate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float) and math.isfinite(node.value) and abs(node.value) <= 1e6:
            return
        if isinstance(node, ast.Name) and node.id in ('x','pi','e'):
            return
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd,ast.USub)):
            validate(node.operand); return
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            validate(node.left); validate(node.right)
            if isinstance(node.op,ast.Pow):
                exponent=node.right
                if isinstance(exponent,ast.UnaryOp): exponent=exponent.operand
                if not isinstance(exponent,ast.Constant) or abs(exponent.value)>12:
                    raise ValueError('Use constant exponents between -12 and 12.')
            return
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in _FUNCTIONS and len(node.args)==1 and not node.keywords:
            validate(node.args[0]); return
        raise ValueError('Use x, numbers, + - * / ^, sin, cos, tan, sqrt, abs, log, or exp.')
    validate(tree.body)
    return tree.body

def evaluate(node, x):
    if isinstance(node,ast.Constant): result=node.value
    elif isinstance(node,ast.Name): result={'x':x,'pi':math.pi,'e':math.e}[node.id]
    elif isinstance(node,ast.UnaryOp): result=(-1 if isinstance(node.op,ast.USub) else 1)*evaluate(node.operand,x)
    elif isinstance(node,ast.BinOp): result=_OPS[type(node.op)](evaluate(node.left,x),evaluate(node.right,x))
    else: result=_FUNCTIONS[node.func.id](evaluate(node.args[0],x))
    if isinstance(result,complex) or not math.isfinite(result) or abs(result)>1e12:
        raise ValueError('Result out of range.')
    return result

def sample_graph(command: CreateGraph):
    tree=parse_expression(command.expression)
    segments=[]; current=[]
    for i in range(401):
        x=command.x_min+(command.x_max-command.x_min)*i/400
        try:
            y=evaluate(tree,x)
            if not command.y_min <= y <= command.y_max: raise ValueError('Offscreen')
            px=50+(x-command.x_min)/(command.x_max-command.x_min)*600
            py=350-(y-command.y_min)/(command.y_max-command.y_min)*300
            if current and abs(py-current[-1]['y'])>100:
                if len(current)>1: segments.append(current)
                current=[]
            current.append({'x':round(px,3),'y':round(py,3)})
        except (ValueError,ArithmeticError,TypeError):
            if len(current)>1: segments.append(current)
            current=[]
    if len(current)>1: segments.append(current)
    if not segments: raise ValueError('No visible graph in these ranges. Try a wider y range.')
    return segments
