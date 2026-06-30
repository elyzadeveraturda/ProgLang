"""
interpreter.py
Execution — Phase 5 (running it for real), Phase 6 (control flow),
Phase 8 (object construction).

Walks the same AST that parser.py builds and semantic.py already
validated. Unlike semantic.py, this module's SymbolTable holds REAL
runtime values (5, "hello", True, an Instance) instead of type strings
— it's a brand new SymbolTable instance, not the one semantic.py used.
"""

from ast_nodes import VarDecl, FuncDecl, ClassDecl


class RuntimeError(Exception):
    """Raised for any problem that only shows up at runtime: division by
    zero, calling something that isn't callable, etc."""
    pass


class _ReturnSignal(Exception):
    """Internal control-flow signal for `return` — not a user-facing
    error. Carries the return value back up to whichever _call_function
    is waiting for it."""
    def __init__(self, value):
        self.value = value


class Instance:
    """Runtime object created by `ClassName(...)`. class_decl is the AST
    node it was built from (used to find fields/methods); fields holds
    its current field values."""
    def __init__(self, class_decl):
        self.class_decl = class_decl
        self.fields = {}

    def __repr__(self):
        return f"<{self.class_decl.name} instance>"


class Interpreter:
    def __init__(self):
        from symbol_table import SymbolTable
        self.symbol_table = SymbolTable()
        self.output = []  # collects each print() statement's output

    def run(self, program):
        for stmt in program.statements:
            self._execute(stmt)
        return self.output

    # ---------- dispatch ----------

    def _execute(self, node):
        method = getattr(self, f"_exec_{type(node).__name__}", None)
        if method is None:
            raise RuntimeError(f"Internal Error: no execution rule for {type(node).__name__}")
        return method(node)

    def _evaluate(self, node):
        method = getattr(self, f"_eval_{type(node).__name__}", None)
        if method is None:
            raise RuntimeError(f"Internal Error: no evaluation rule for {type(node).__name__}")
        return method(node)

    # ---------- statements ----------

    def _exec_VarDecl(self, node):
        value = self._evaluate(node.value) if node.value is not None else None
        self.symbol_table.define(node.name, value=value, type_annotation=node.type_annotation, is_let=node.is_let)

    def _exec_FuncDecl(self, node):
        self.symbol_table.define(node.name, value=node, type_annotation=node.return_type, is_let=True)

    def _exec_ClassDecl(self, node):
        self.symbol_table.define(node.name, value=node, type_annotation=node.name, is_let=True)

    def _exec_Block(self, node):
        self.symbol_table.push_scope()
        try:
            for stmt in node.statements:
                self._execute(stmt)
        finally:
            self.symbol_table.pop_scope()

    def _exec_IfStmt(self, node):
        if self._evaluate(node.condition):
            self._execute(node.then_branch)
        elif node.else_branch is not None:
            self._execute(node.else_branch)  # Block, or another IfStmt (else-if)

    def _exec_WhileStmt(self, node):
        while self._evaluate(node.condition):
            self._execute(node.body)

    def _exec_ForStmt(self, node):
        self.symbol_table.push_scope()
        try:
            if node.init is not None:
                self._execute(node.init)
            while node.condition is None or self._evaluate(node.condition):
                self._execute(node.body)
                if node.update is not None:
                    self._evaluate(node.update)
        finally:
            self.symbol_table.pop_scope()

    def _exec_ReturnStmt(self, node):
        value = self._evaluate(node.value) if node.value is not None else None
        raise _ReturnSignal(value)

    def _exec_PrintStmt(self, node):
        # CHANGE: print() now accepts multiple comma-separated arguments,
        # e.g. print("x =", x). Each is evaluated, stringified, and the
        # results are joined with a single space — matching how parser.py
        # now builds PrintStmt.values as a list instead of one .value.
        parts = [self._stringify(self._evaluate(v)) for v in node.values]
        self.output.append(" ".join(parts))

    def _exec_ExprStmt(self, node):
        self._evaluate(node.expression)

    # ---------- expressions ----------

    def _eval_Literal(self, node):
        return node.value

    def _eval_Identifier(self, node):
        from symbol_table import SymbolTableError
        try:
            return self.symbol_table.lookup(node.name)
        except SymbolTableError as e:
            raise RuntimeError(str(e))

    def _eval_BinaryOp(self, node):
        left = self._evaluate(node.left)
        right = self._evaluate(node.right)
        op = node.operator

        try:
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                if right == 0:
                    raise RuntimeError("Runtime Error: division by zero")
                # Int / Int stays Int (matches semantic.py's result-type
                # rule); anything involving a Float divides normally.
                if isinstance(left, int) and isinstance(right, int):
                    return left // right
                return left / right
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
            if op == "<":
                return left < right
            if op == ">":
                return left > right
            if op == "<=":
                return left <= right
            if op == ">=":
                return left >= right
        except TypeError:
            raise RuntimeError(f"Runtime Error: cannot apply '{op}' to {left!r} and {right!r}")

        raise RuntimeError(f"Internal Error: unknown operator '{op}'")

    def _eval_UnaryOp(self, node):
        operand = self._evaluate(node.operand)
        return -operand if node.operator == "-" else operand

    # CHANGE: new method — evaluates 'and' / 'or' / 'not' with proper
    # short-circuit behavior (the right side of 'and'/'or' is only
    # evaluated if needed), matching how every other language does it.
    def _eval_LogicalOp(self, node):
        if node.operator == "not":
            return not self._evaluate(node.right)

        left = self._evaluate(node.left)
        if node.operator == "and":
            if not left:
                return False  # short-circuit: right side never evaluated
            return bool(self._evaluate(node.right))

        if node.operator == "or":
            if left:
                return True  # short-circuit: right side never evaluated
            return bool(self._evaluate(node.right))

        raise RuntimeError(f"Internal Error: unknown logical operator '{node.operator}'")

    def _eval_Assignment(self, node):
        from symbol_table import SymbolTableError
        value = self._evaluate(node.value)
        try:
            self.symbol_table.assign(node.target, value)
        except SymbolTableError as e:
            raise RuntimeError(str(e))
        return value

    def _eval_FunctionCall(self, node):
        from symbol_table import SymbolTableError
        try:
            target = self.symbol_table.lookup(node.callee)
        except SymbolTableError as e:
            raise RuntimeError(str(e))

        args = [self._evaluate(arg) for arg in node.arguments]

        if isinstance(target, ClassDecl):
            return self._construct_instance(target, args)
        if isinstance(target, FuncDecl):
            return self._call_function(target, args)

        raise RuntimeError(f"Runtime Error: '{node.callee}' is not callable")
    
    def _eval_MemberAccess(self, node):
        """rex.name — reads a field off an instance."""
        obj = self._evaluate(node.obj)
        if not isinstance(obj, Instance):
            raise RuntimeError(f"Runtime Error: cannot access '.{node.member}' on a non-object value")
        if node.member not in obj.fields:
            raise RuntimeError(f"Runtime Error: '{obj.class_decl.name}' has no field '{node.member}'")
        return obj.fields[node.member]

    def _eval_MethodCall(self, node):
        """rex.speak() — calls a method on an instance. Reuses
        _call_function's field_scope mechanism, same as init() does
        during construction, so the method body can read/write fields
        by bare name (no `self.`)."""
        obj = self._evaluate(node.obj)
        if not isinstance(obj, Instance):
            raise RuntimeError(f"Runtime Error: cannot call '.{node.method}()' on a non-object value")

        method = next(
            (m for m in obj.class_decl.members if isinstance(m, FuncDecl) and m.name == node.method), None
        )
        if method is None:
            raise RuntimeError(f"Runtime Error: '{obj.class_decl.name}' has no method '{node.method}'")

        args = [self._evaluate(arg) for arg in node.arguments]
        return self._call_function(method, args, field_scope=obj.fields)

    # ---------- function & constructor calls ----------

    def _call_function(self, func_decl, args, field_scope=None):
        """field_scope: only used when calling init() during object
        construction. It's the instance's .fields dict, pre-loaded into
        this call's scope so init()'s body can read/write fields by bare
        name (no `self.`) — matching the no-self style in the project's
        own class example. After the call, the updated values are copied
        back into field_scope so they persist on the instance."""
        self.symbol_table.push_scope()
        try:
            if field_scope is not None:
                for name, value in field_scope.items():
                    self.symbol_table.define(name, value=value)

            for param, arg_value in zip(func_decl.params, args):
                self.symbol_table.define(param.name, value=arg_value)

            try:
                for stmt in func_decl.body.statements:
                    self._execute(stmt)
                result = None
            except _ReturnSignal as signal:
                result = signal.value

            if field_scope is not None:
                self._sync_field_scope_back(field_scope)
            return result
        finally:
            self.symbol_table.pop_scope()

    def _sync_field_scope_back(self, field_scope):
        for name in field_scope:
            if self.symbol_table.exists(name):
                field_scope[name] = self.symbol_table.lookup(name)

    def _construct_instance(self, class_decl, args):
        instance = Instance(class_decl)

        for member in class_decl.members:
            if isinstance(member, VarDecl):
                instance.fields[member.name] = self._evaluate(member.value) if member.value is not None else None

        init_method = next(
            (m for m in class_decl.members if isinstance(m, FuncDecl) and m.name == "init"), None
        )
        if init_method is not None:
            self._call_function(init_method, args, field_scope=instance.fields)
        elif args:
            raise RuntimeError(
                f"Runtime Error: '{class_decl.name}' has no init() but was called with arguments"
            )

        return instance

    # ---------- helpers ----------

    def _stringify(self, value):
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return "null"
        return str(value)