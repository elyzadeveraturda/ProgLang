"""
semantic.py
Semantic Analysis — Phase 5, plus Data Types — Phase 7.

Walks the AST that parser.py builds, using symbol_table.py to track
declarations and scope, and checks:
  - every name used is actually declared (Phase 4 enforcement)
  - every operation is applied to compatible types (Phase 5)
  - basic type conversion rules for Int / Float / String / Bool (Phase 7)

IMPORTANT: this module's SymbolTable stores TYPE STRINGS in the `value`
field (e.g. "Int", "String"), not real runtime values — semantic
analysis happens before the program actually runs. interpreter.py will
create its OWN SymbolTable instance later, where `value` holds real
runtime values (5, "hello", True, etc).

Usage from compiler.py:

    from semantic import SemanticAnalyzer, SemanticError

    try:
        symbol_table = SemanticAnalyzer().check(ast)
    except SemanticError as e:
        ...
"""

from ast_nodes import (
    VarDecl, FuncDecl, ClassDecl, Block, IfStmt, WhileStmt, ForStmt,
    ReturnStmt, PrintStmt, ExprStmt,
)
from symbol_table import SymbolTable


class SemanticError(Exception):
    """Raised for any type or declaration problem. compiler.py catches
    this the same way it catches LexerError / ParserError."""
    pass


KNOWN_TYPES = {"Int", "Float", "String", "Bool"}
NUMERIC_TYPES = {"Int", "Float"}

# Params/returns with no annotation are treated as this wildcard type —
# compatible with everything. Keeps the type system simple for a teaching
# project instead of requiring full type inference.
ANY_TYPE = "Any"


class SemanticAnalyzer:
    def __init__(self, symbol_table=None):
        self.symbol_table = symbol_table or SymbolTable()
        # Tracks the expected return type of whichever function we're
        # currently inside, so `return` statements can be checked.
        # None at the top level (outside any function).
        self._return_type_stack = []

    def check(self, program):
        """Entry point: type-checks every top-level statement.
        Returns the populated SymbolTable for compiler.py / later phases
        to inspect if needed."""
        for stmt in program.statements:
            self._check_statement(stmt)
        return self.symbol_table

    # ---------- dispatch helpers ----------

    def _check_statement(self, node):
        method = getattr(self, f"_check_{type(node).__name__}", None)
        if method is None:
            raise SemanticError(f"Internal Error: no semantic rule for {type(node).__name__}")
        return method(node)

    def _infer_type(self, node):
        """Returns the type string for an expression node, e.g. 'Int'."""
        method = getattr(self, f"_infer_{type(node).__name__}", None)
        if method is None:
            raise SemanticError(f"Internal Error: no type rule for {type(node).__name__}")
        return method(node)

    # ---------- type compatibility ----------

    def _check_type_compatible(self, declared, actual, context):
        """declared = the type something is supposed to be (annotation,
        param type, return type). actual = the type it's actually getting.
        Allows Int -> Float widening; everything else must match exactly."""
        if declared == ANY_TYPE or actual == ANY_TYPE:
            return
        if declared == actual:
            return
        if declared == "Float" and actual == "Int":
            return  # widening: a Float-typed slot can hold an Int value
        raise SemanticError(f"Type Error: cannot assign {actual} to {context} of type {declared}")

    def _binary_result_type(self, op, left_type, right_type):
        if left_type == ANY_TYPE or right_type == ANY_TYPE:
            return ANY_TYPE

        if op in ("+", "-", "*", "/"):
            if op == "+" and left_type == "String" and right_type == "String":
                return "String"  # string concatenation
            if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                return "Float" if "Float" in (left_type, right_type) else "Int"
            raise SemanticError(f"Type Error: cannot apply '{op}' to {left_type} and {right_type}")

        if op in ("<", ">", "<=", ">="):
            if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                return "Bool"
            raise SemanticError(f"Type Error: cannot compare {left_type} and {right_type} with '{op}'")

        if op in ("==", "!="):
            same_category = left_type == right_type or (
                left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES
            )
            if same_category:
                return "Bool"
            raise SemanticError(f"Type Error: cannot compare {left_type} and {right_type} for equality")

        raise SemanticError(f"Internal Error: unknown operator '{op}'")

    # ---------- statements ----------

    def _check_VarDecl(self, node):
        if node.type_annotation is not None and node.type_annotation not in KNOWN_TYPES:
            raise SemanticError(
                f"Type Error: unknown type '{node.type_annotation}' for variable '{node.name}'"
            )

        value_type = self._infer_type(node.value) if node.value is not None else None

        if node.type_annotation is not None and value_type is not None:
            self._check_type_compatible(node.type_annotation, value_type, f"variable '{node.name}'")
            declared_type = node.type_annotation
        elif node.type_annotation is not None:
            declared_type = node.type_annotation        # e.g. `var x: Int;` — no initial value yet
        elif value_type is not None:
            declared_type = value_type                  # e.g. `let y = 10;` — infer from value
        else:
            raise SemanticError(
                f"Type Error: variable '{node.name}' needs either a type annotation or an initial value"
            )

        self.symbol_table.define(node.name, value=declared_type, type_annotation=declared_type, is_let=node.is_let)

    def _check_FuncDecl(self, node):
        # Register the function in the ENCLOSING scope first, so it can
        # call itself recursively, and so sibling functions can call it.
        self.symbol_table.define(node.name, value=node, type_annotation=node.return_type, is_let=True)

        self.symbol_table.push_scope()
        for param in node.params:
            ptype = param.type_annotation or ANY_TYPE
            self.symbol_table.define(param.name, value=ptype, type_annotation=ptype, is_let=False)

        self._return_type_stack.append(node.return_type)
        self._check_Block(node.body)
        self._return_type_stack.pop()

        self.symbol_table.pop_scope()

    def _check_ClassDecl(self, node):
        self.symbol_table.define(node.name, value=node, type_annotation=node.name, is_let=True)

        # Class-level scope holds fields. Pushed BEFORE checking methods,
        # so a method body (e.g. init's `name = n;`) can see fields
        # declared in this same class — matches the example in the
        # README where init() assigns directly to a field with no `self`.
        self.symbol_table.push_scope()
        for member in node.members:
            if isinstance(member, VarDecl):
                self._check_VarDecl(member)
            elif isinstance(member, FuncDecl):
                self._check_FuncDecl(member)
            else:
                raise SemanticError(f"Internal Error: unexpected class member {type(member).__name__}")
        self.symbol_table.pop_scope()

    def _check_Block(self, node):
        self.symbol_table.push_scope()
        for stmt in node.statements:
            self._check_statement(stmt)
        self.symbol_table.pop_scope()

    def _check_IfStmt(self, node):
        cond_type = self._infer_type(node.condition)
        if cond_type not in ("Bool", ANY_TYPE):
            raise SemanticError(f"Type Error: if condition must be a Bool, got {cond_type}")

        self._check_Block(node.then_branch)
        if node.else_branch is not None:
            if isinstance(node.else_branch, Block):
                self._check_Block(node.else_branch)
            else:
                self._check_IfStmt(node.else_branch)  # else-if chain

    def _check_WhileStmt(self, node):
        cond_type = self._infer_type(node.condition)
        if cond_type not in ("Bool", ANY_TYPE):
            raise SemanticError(f"Type Error: while condition must be a Bool, got {cond_type}")
        self._check_Block(node.body)

    def _check_ForStmt(self, node):
        # Own scope so a `for (var i: Int = 0; ...)` loop variable
        # doesn't leak into the surrounding code.
        self.symbol_table.push_scope()

        if node.init is not None:
            self._check_statement(node.init)

        if node.condition is not None:
            cond_type = self._infer_type(node.condition)
            if cond_type not in ("Bool", ANY_TYPE):
                raise SemanticError(f"Type Error: for-loop condition must be a Bool, got {cond_type}")

        if node.update is not None:
            self._infer_type(node.update)

        self._check_Block(node.body)
        self.symbol_table.pop_scope()

    def _check_ReturnStmt(self, node):
        if not self._return_type_stack:
            raise SemanticError("Syntax Error: 'return' used outside of a function")

        expected = self._return_type_stack[-1]

        if node.value is not None:
            actual = self._infer_type(node.value)
            if expected is not None:
                self._check_type_compatible(expected, actual, "the function's return value")
        elif expected is not None:
            raise SemanticError(f"Type Error: function must return a value of type {expected}")

    def _check_PrintStmt(self, node):
        self._infer_type(node.value)  # any type is printable — just must type-check cleanly

    def _check_ExprStmt(self, node):
        self._infer_type(node.expression)

    # ---------- expressions ----------

    def _infer_Literal(self, node):
        return node.literal_type

    def _infer_Identifier(self, node):
        symbol = self.symbol_table.get_symbol(node.name)  # raises SymbolTableError if undefined
        return symbol.type_annotation or ANY_TYPE

    def _infer_BinaryOp(self, node):
        left_type = self._infer_type(node.left)
        right_type = self._infer_type(node.right)
        return self._binary_result_type(node.operator, left_type, right_type)

    def _infer_UnaryOp(self, node):
        operand_type = self._infer_type(node.operand)
        if operand_type in NUMERIC_TYPES or operand_type == ANY_TYPE:
            return operand_type
        raise SemanticError(
            f"Type Error: unary '{node.operator}' requires a numeric operand, got {operand_type}"
        )

    def _infer_Assignment(self, node):
        symbol = self.symbol_table.get_symbol(node.target)  # raises SymbolTableError if undefined
        value_type = self._infer_type(node.value)
        self._check_type_compatible(symbol.type_annotation or ANY_TYPE, value_type, f"variable '{node.target}'")
        self.symbol_table.assign(node.target, value_type)   # also enforces `let` immutability
        return symbol.type_annotation or ANY_TYPE

    def _infer_FunctionCall(self, node):
        symbol = self.symbol_table.get_symbol(node.callee)  # raises SymbolTableError if undefined

        if isinstance(symbol.value, FuncDecl):
            func = symbol.value
            if len(node.arguments) != len(func.params):
                raise SemanticError(
                    f"Type Error: '{node.callee}' expects {len(func.params)} argument(s), "
                    f"got {len(node.arguments)}"
                )
            for arg_node, param in zip(node.arguments, func.params):
                arg_type = self._infer_type(arg_node)
                expected = param.type_annotation or ANY_TYPE
                self._check_type_compatible(expected, arg_type, f"argument '{param.name}' of '{node.callee}'")
            return func.return_type or ANY_TYPE

        if isinstance(symbol.value, ClassDecl):
            # Object construction, e.g. Animal("Rex"). Checked against
            # init() if the class defines one; skipped if it doesn't —
            # full constructor enforcement is left for interpreter.py.
            cls = symbol.value
            init_method = next(
                (m for m in cls.members if isinstance(m, FuncDecl) and m.name == "init"), None
            )
            if init_method is not None:
                if len(node.arguments) != len(init_method.params):
                    raise SemanticError(
                        f"Type Error: '{node.callee}' constructor expects "
                        f"{len(init_method.params)} argument(s), got {len(node.arguments)}"
                    )
                for arg_node, param in zip(node.arguments, init_method.params):
                    arg_type = self._infer_type(arg_node)
                    expected = param.type_annotation or ANY_TYPE
                    self._check_type_compatible(expected, arg_type, f"argument '{param.name}' of '{node.callee}'")
            return cls.name  # the resulting type is "an instance of this class"

        raise SemanticError(f"Type Error: '{node.callee}' is not callable")
    
    def _get_class_decl(self, type_name, member_name):
        """Resolves a type name (e.g. "Animal") to its ClassDecl, so
        MemberAccess/MethodCall can look up fields/methods on it.
        Raises a clear error if the type isn't actually a class — this
        is what catches things like trying to do `5.name` or accessing
        a field on a function's return value when it wasn't a class."""
        if not self.symbol_table.exists(type_name):
            raise SemanticError(f"Type Error: '{type_name}' is not a class, cannot access '.{member_name}'")
        symbol = self.symbol_table.get_symbol(type_name)
        if not isinstance(symbol.value, ClassDecl):
            raise SemanticError(f"Type Error: '{type_name}' is not a class, cannot access '.{member_name}'")
        return symbol.value

    def _infer_MemberAccess(self, node):
        obj_type = self._infer_type(node.obj)
        if obj_type == ANY_TYPE:
            return ANY_TYPE

        class_decl = self._get_class_decl(obj_type, node.member)
        for member in class_decl.members:
            if isinstance(member, VarDecl) and member.name == node.member:
                return member.type_annotation or ANY_TYPE

        raise SemanticError(f"Type Error: '{obj_type}' has no field '{node.member}'")

    def _infer_MethodCall(self, node):
        obj_type = self._infer_type(node.obj)
        if obj_type == ANY_TYPE:
            for arg in node.arguments:
                self._infer_type(arg)
            return ANY_TYPE

        class_decl = self._get_class_decl(obj_type, node.method)
        method = next(
            (m for m in class_decl.members if isinstance(m, FuncDecl) and m.name == node.method), None
        )
        if method is None:
            raise SemanticError(f"Type Error: '{obj_type}' has no method '{node.method}'")

        if len(node.arguments) != len(method.params):
            raise SemanticError(
                f"Type Error: '{node.method}' expects {len(method.params)} argument(s), "
                f"got {len(node.arguments)}"
            )
        for arg_node, param in zip(node.arguments, method.params):
            arg_type = self._infer_type(arg_node)
            expected = param.type_annotation or ANY_TYPE
            self._check_type_compatible(expected, arg_type, f"argument '{param.name}' of '{node.method}'")

        return method.return_type or ANY_TYPE