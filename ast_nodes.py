"""
ast_nodes.py
AST node definitions for MiniLang.

CHANGES FROM ORIGINAL:
  1. Added LogicalOp node for 'and' / 'or' / 'not' expressions.
  2. PrintStmt.value changed to PrintStmt.values (a List) so
     print("x =", x) works with multiple arguments.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any


# ---------- Top-level ----------

@dataclass
class Program:
    statements: List[Any] = field(default_factory=list)


# ---------- Declarations ----------

@dataclass
class VarDecl:
    name: str
    type_annotation: Optional[str]
    value: Optional[Any]
    is_let: bool = False


@dataclass
class Param:
    name: str
    type_annotation: Optional[str]


@dataclass
class FuncDecl:
    name: str
    params: List[Param]
    return_type: Optional[str]
    body: "Block"


@dataclass
class ClassDecl:
    name: str
    members: List[Any] = field(default_factory=list)


# ---------- Statements ----------

@dataclass
class Block:
    statements: List[Any] = field(default_factory=list)


@dataclass
class IfStmt:
    condition: Any
    then_branch: Block
    else_branch: Optional[Any] = None


@dataclass
class WhileStmt:
    condition: Any
    body: Block


@dataclass
class ForStmt:
    init: Optional[Any]
    condition: Optional[Any]
    update: Optional[Any]
    body: Block


@dataclass
class ReturnStmt:
    value: Optional[Any] = None


@dataclass
class PrintStmt:
    # CHANGE 2: was `value: Any` — now a list so print("a", b, c) works
    values: List[Any] = field(default_factory=list)


@dataclass
class ExprStmt:
    expression: Any


# ---------- Expressions ----------

@dataclass
class Assignment:
    target: str
    value: Any


@dataclass
class BinaryOp:
    left: Any
    operator: str
    right: Any


# CHANGE 1: new node for 'and' / 'or' / 'not'
@dataclass
class LogicalOp:
    """Logical operators: 'and', 'or' (binary) and 'not' (unary).
    For 'not', left is None and right holds the operand."""
    operator: str   # 'and' | 'or' | 'not'
    left: Optional[Any]   # None for 'not'
    right: Any


@dataclass
class UnaryOp:
    operator: str
    operand: Any


@dataclass
class Literal:
    value: Any
    literal_type: str


@dataclass
class Identifier:
    name: str


@dataclass
class FunctionCall:
    callee: str
    arguments: List[Any] = field(default_factory=list)


@dataclass
class MemberAccess:
    obj: Any
    member: str


@dataclass
class MethodCall:
    obj: Any
    method: str
    arguments: List[Any] = field(default_factory=list)
