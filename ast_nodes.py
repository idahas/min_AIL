"""AST Node definitions for the Min language."""

from dataclasses import dataclass, field
from typing import Any


class Node:
    """Base AST node."""
    line: int = 0
    col: int = 0


# ─── Literals ────────────────────────────────────────────────

@dataclass
class Number(Node):
    value: float | int

@dataclass
class String(Node):
    value: str

@dataclass
class Boolean(Node):
    value: bool

@dataclass
class Null(Node):
    pass

@dataclass
class Array(Node):
    elements: list[Node]

@dataclass
class Object(Node):
    pairs: dict[str, Node]


# ─── Expressions ─────────────────────────────────────────────

@dataclass
class Identifier(Node):
    name: str

@dataclass
class BinaryOp(Node):
    op: str
    left: Node
    right: Node

@dataclass
class UnaryOp(Node):
    op: str
    operand: Node

@dataclass
class Assignment(Node):
    name: Node  # Identifier or DotAccess
    value: Node

@dataclass
class DotAccess(Node):
    object: Node
    member: str

@dataclass
class IndexAccess(Node):
    object: Node
    index: Node

@dataclass
class FunctionCall(Node):
    callee: Node  # Identifier or DotAccess
    args: list[Node]


# ─── Statements ──────────────────────────────────────────────

@dataclass
class If(Node):
    condition: Node
    then_body: list[Node]
    else_body: list[Node] | None = None

@dataclass
class While(Node):
    condition: Node
    body: list[Node]

@dataclass
class For(Node):
    var: str
    start: Node
    end: Node
    body: list[Node]

@dataclass
class Break(Node):
    pass

@dataclass
class Continue(Node):
    pass

@dataclass
class Return(Node):
    value: Node | None = None


from dataclasses import dataclass, field

@dataclass
class MultiAssignment(Node):
    targets: list[str]
    value: Node

@dataclass
class ListComprehension(Node):
    var_name: str
    iterable: Node
    expr: Node
    condition: Node | None = None


# ─── Functions & Classes ─────────────────────────────────────

@dataclass
class FunctionDef(Node):
    name: str
    params: list[str]
    body: list[Node]
    defaults: dict[str, Node] = field(default_factory=dict)
    vararg: str | None = None

@dataclass
class ClassDef(Node):
    name: str
    super_class: str | None
    fields: dict[str, Node]
    methods: list[FunctionDef]
    init_method: FunctionDef | None = None

@dataclass
class ObjectInit(Node):
    class_name: str
    args: list[Node]


# ─── I/O & Modules ──────────────────────────────────────────

@dataclass
class Print(Node):
    args: list[Node]

@dataclass
class Input(Node):
    prompt: Node | None = None

@dataclass
class Import(Node):
    module: str
    alias: str | None = None

@dataclass
class Export(Node):
    name: str


# ─── Error Handling ─────────────────────────────────────────

@dataclass
class TryCatch(Node):
    try_body: list[Node]
    catch_var: str
    catch_body: list[Node]

@dataclass
class Throw(Node):
    message: Node


# ─── Pattern Matching ─────────────────────────────────────────

@dataclass
class MatchCase(Node):
    pattern: Node
    body: list[Node]

@dataclass
class Match(Node):
    expr: Node
    cases: list[MatchCase]
    default_body: list[Node] | None = None


# ─── Root ────────────────────────────────────────────────────

@dataclass
class Program(Node):
    statements: list[Node]
    filename: str = "<input>"
