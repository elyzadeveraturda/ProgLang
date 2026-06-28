"""
ast_nodes.py
Abstract Syntax Tree (AST) node definitions for MiniLang — Phase 3.

These are the "nouns" of the language. parser.py builds a tree of these
nodes from the token stream; symbol_table.py / semantic.py / interpreter.py
will later walk this same tree to check and run the program.

Each node is a plain dataclass — no behavior, just structured data. That
keeps parser.py focused on *building* the tree, and lets the later phases
add their own logic (e.g. dispatch on type(node).__name__) without this
file needing to change.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any


# ---------- Top-level ----------

@dataclass
class Program:
    """Root node. A MiniLang file is just a list of top-level statements."""
    statements: List[Any] = field(default_factory=list)


# ---------- Declarations ----------

@dataclass
class VarDecl:
    """var x: Int = 5;   or   let y = 10;
    type_annotation is None when omitted (e.g. `let y = 10;`)."""
    name: str
    type_annotation: Optional[str]
    value: Optional[Any]
    is_let: bool = False


@dataclass
class Param:
    """A single function parameter: `who: String`"""
    name: str
    type_annotation: Optional[str]


@dataclass
class FuncDecl:
    """func greet(who: String): String { ... }"""
    name: str
    params: List[Param]
    return_type: Optional[str]
    body: "Block"


@dataclass
class ClassDecl:
    """class Animal { var name: String; func init(n: String) { ... } }
    members is a mixed list of VarDecl (fields) and FuncDecl (methods)."""
    name: str
    members: List[Any] = field(default_factory=list)


# ---------- Statements ----------

@dataclass
class Block:
    """A `{ ... }` body."""
    statements: List[Any] = field(default_factory=list)


@dataclass
class IfStmt:
    condition: Any
    then_branch: Block
    else_branch: Optional[Any] = None  # Block or another IfStmt (else-if chains)


@dataclass
class WhileStmt:
    condition: Any
    body: Block


@dataclass
class ForStmt:
    """for (init; condition; update) { body }"""
    init: Optional[Any]
    condition: Optional[Any]
    update: Optional[Any]
    body: Block


@dataclass
class ReturnStmt:
    value: Optional[Any] = None


@dataclass
class PrintStmt:
    value: Any


@dataclass
class ExprStmt:
    """A bare expression used as a statement, e.g. `x = x + 1;`"""
    expression: Any


# ---------- Expressions ----------

@dataclass
class Assignment:
    target: str
    value: Any


@dataclass
class BinaryOp:
    left: Any
    operator: str   # '+', '-', '*', '/', '==', '<', '>'
    right: Any


@dataclass
class UnaryOp:
    operator: str   # '-' or '+'
    operand: Any


@dataclass
class Literal:
    value: Any
    literal_type: str  # 'Int' | 'Float' | 'String' | 'Bool'


@dataclass
class Identifier:
    name: str


@dataclass
class FunctionCall:
    """greet("World") — also doubles as object construction (Animal("Rex")),
    since at parse time we can't yet tell a function name from a class name."""
    callee: str
    arguments: List[Any] = field(default_factory=list)


@dataclass
class MemberAccess:
    """obj.field — reads a field on an instance, e.g. `rex.name`."""
    obj: Any
    member: str


@dataclass
class MethodCall:
    """obj.method(args) — calls a method on an instance, e.g. `rex.speak()`."""
    obj: Any
    method: str
    arguments: List[Any] = field(default_factory=list)