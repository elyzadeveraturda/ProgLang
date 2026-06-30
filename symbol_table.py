"""
symbol_table.py
Names, Scope, and Binding — Phase 4.

Tracks what variables (and later, functions/classes) exist, what values
they hold, and which scope they belong to. This file doesn't run on its
own — semantic.py and interpreter.py (still empty) will create a
SymbolTable instance and call into it while they walk the AST.

Scoping model: a stack of dictionaries. scopes[0] is global and is never
popped. Entering a function body or a block pushes a new dict; leaving
it pops that dict. Lookups walk innermost -> outermost, matching normal
lexical scoping rules.
"""


class SymbolTableError(Exception):
    """Raised for any scope/binding problem: undefined name, redeclaration
    in the same scope, or reassigning a `let` binding."""
    pass


class _Symbol:
    """Internal record for one binding."""
    __slots__ = ("name", "value", "type_annotation", "is_let")

    def __init__(self, name, value, type_annotation=None, is_let=False):
        self.name = name
        self.value = value
        self.type_annotation = type_annotation
        self.is_let = is_let


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # scopes[0] = global scope

    # ---------- scope management ----------

    def push_scope(self):
        """Call when entering a new block: function body, if/while/for body."""
        self.scopes.append({})

    def pop_scope(self):
        """Call when leaving that block. Never pops the global scope."""
        if len(self.scopes) == 1:
            raise SymbolTableError("Internal Error: cannot pop the global scope")
        self.scopes.pop()

    @property
    def current_scope(self):
        return self.scopes[-1]

    # ---------- declaring ----------

    def define(self, name, value, type_annotation=None, is_let=False):
        """Declare a new binding in the CURRENT (innermost) scope.
        Matches VarDecl from ast_nodes.py: `var x: Int = 5;` / `let y = 10;`
        Also used for FuncDecl / ClassDecl — store the node itself as the
        value, with is_let=True, so functions/classes can't be reassigned."""
        if name in self.current_scope:
            raise SymbolTableError(
                f"Name Error: '{name}' is already declared in this scope"
            )
        self.current_scope[name] = _Symbol(name, value, type_annotation, is_let)

    # ---------- looking up / assigning ----------

    def _find_scope(self, name):
        """Search scopes innermost -> outermost. Returns the dict holding
        `name`, or None if not found anywhere."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope
        return None

    def lookup(self, name):
        """Return the current value bound to `name`. Used by interpreter.py
        when evaluating an Identifier node."""
        scope = self._find_scope(name)
        if scope is None:
            raise SymbolTableError(f"Name Error: '{name}' is not defined")
        return scope[name].value

    def get_symbol(self, name):
        """Return the full _Symbol record (value + type + mutability),
        used by semantic.py for type checking."""
        scope = self._find_scope(name)
        if scope is None:
            raise SymbolTableError(f"Name Error: '{name}' is not defined")
        return scope[name]

    def exists(self, name):
        return self._find_scope(name) is not None

    def assign(self, name, value):
        """Update an EXISTING binding — for `x = x + 1;` style Assignment
        nodes, not declarations. Enforces `let` immutability."""
        scope = self._find_scope(name)
        if scope is None:
            raise SymbolTableError(f"Name Error: '{name}' is not defined")
        symbol = scope[name]
        if symbol.is_let:
            raise SymbolTableError(
                f"Name Error: cannot reassign '{name}', it was declared with 'let'"
            )
        symbol.value = value

    def to_dict(self):
        # CHANGE: stringify FuncDecl / ClassDecl values instead of returning
        # the raw AST dataclass object. Previously a function or class
        # symbol's "value" field held the actual FuncDecl/ClassDecl node,
        # which the JSON serializer in serializer.py / Flask's jsonify()
        # can't handle and would crash on. Plain Int/String/Bool/Float
        # symbols already store a type-string in `value`, so those are
        # left untouched.
        from ast_nodes import FuncDecl, ClassDecl

        result = []

        for scope_index, scope in enumerate(self.scopes):

            scope_name = "global" if scope_index == 0 else "local"

            for symbol in scope.values():

                if isinstance(symbol.value, FuncDecl):
                    display_value = f"<function {symbol.value.name}>"
                elif isinstance(symbol.value, ClassDecl):
                    display_value = f"<class {symbol.value.name}>"
                else:
                    display_value = symbol.value

                result.append({

                    "name": symbol.name,

                    "type": symbol.type_annotation,

                    "value": display_value,

                    "scope": scope_name,

                    "mutable": not symbol.is_let

                })

        return result