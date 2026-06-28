"""
parser.py
Syntax Analysis — Phase 3 (plus the syntax half of Phase 6: control flow).

Takes the flat token list from lexer.py's tokenizer (the same
{"type": ..., "value": ...} dicts compiler.py already produces) and turns
it into the AST defined in ast_nodes.py.

Usage from compiler.py's orchestrator:

    from lexer import tokenize
    from parser import Parser, ParserError

    tokens = tokenize(source_code)
    try:
        ast = Parser(tokens).parse()
    except ParserError as e:
        # str(e) is already formatted like the lexer's "Lexical Error: ..."
        ...
"""

from ast_nodes import (
    Program, VarDecl, Param, FuncDecl, ClassDecl, Block,
    IfStmt, WhileStmt, ForStmt, ReturnStmt, PrintStmt, ExprStmt,
    Assignment, BinaryOp, UnaryOp, Literal, Identifier, FunctionCall,
    MemberAccess, MethodCall,
)


class ParserError(Exception):
    """Raised on any syntax error. compiler.py catches this and sends it
    to the frontend console, same pattern as the lexer's error messages."""
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---------- low-level token helpers ----------

    def _peek(self, offset=0):
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else None

    def _at_end(self):
        return self.pos >= len(self.tokens)

    def _advance(self):
        tok = self._peek()
        if tok is not None:
            self.pos += 1
        return tok

    def _check_value(self, value, offset=0):
        tok = self._peek(offset)
        return tok is not None and tok["value"] == value

    def _check_type(self, type_, offset=0):
        tok = self._peek(offset)
        return tok is not None and tok["type"] == type_

    def _match_value(self, value):
        if self._check_value(value):
            return self._advance()
        return None

    def _expect_value(self, value):
        tok = self._advance()
        if tok is None or tok["value"] != value:
            self._error(f"expected '{value}'", tok)
        return tok

    def _expect_type(self, type_):
        tok = self._advance()
        if tok is None or tok["type"] != type_:
            self._error(f"expected {type_}", tok)
        return tok

    def _error(self, message, tok=None):
        if tok is not None:
            raise ParserError(f"Syntax Error: {message}, got '{tok['value']}'")
        raise ParserError(f"Syntax Error: {message}, but reached end of input")

    # NOTE: lexer.py's OP regex (`[+\-*/==<>]`) is a character class, so it
    # matches a single '=' twice rather than the two-char token '=='.
    # Until that's fixed in lexer.py, "x == 3" arrives here as two separate
    # single-'=' tokens back-to-back. This helper detects that pattern and
    # treats it as one equality operator so comparisons work today. Once
    # lexer.py emits a real '==' token, delete this and use _match_value
    # directly in _parse_equality().
    def _match_equality_operator(self):
        if self._check_value("=") and self._check_value("=", offset=1):
            self._advance()
            self._advance()
            return "=="
        return None

    # ---------- entry point ----------

    def parse(self):
        statements = []
        while not self._at_end():
            statements.append(self._parse_statement())
        return Program(statements=statements)

    # ---------- statements ----------

    def _parse_statement(self):
        tok = self._peek()
        if tok is None:
            self._error("unexpected end of input")

        value = tok["value"]
        if value in ("var", "let"):
            return self._parse_var_decl()
        if value == "func":
            return self._parse_func_decl()
        if value == "class":
            return self._parse_class_decl()
        if value == "if":
            return self._parse_if()
        if value == "while":
            return self._parse_while()
        if value == "for":
            return self._parse_for()
        if value == "return":
            return self._parse_return()
        if value == "print":
            return self._parse_print()
        if value == "{":
            return self._parse_block()

        return self._parse_expr_statement()

    def _parse_var_decl(self):
        is_let = self._advance()["value"] == "let"  # consumes 'var' or 'let'
        name = self._expect_type("IDENTIFIER")["value"]

        type_annotation = None
        if self._match_value(":"):
            type_annotation = self._advance()["value"]

        value = None
        if self._match_value("="):
            value = self._parse_expression()

        self._expect_value(";")
        return VarDecl(name=name, type_annotation=type_annotation, value=value, is_let=is_let)

    def _parse_func_decl(self):
        self._expect_value("func")
        name = self._expect_type("IDENTIFIER")["value"]
        self._expect_value("(")

        params = []
        if not self._check_value(")"):
            params.append(self._parse_param())
            while self._match_value(","):
                params.append(self._parse_param())
        self._expect_value(")")

        return_type = None
        if self._match_value(":"):
            return_type = self._advance()["value"]

        body = self._parse_block()
        return FuncDecl(name=name, params=params, return_type=return_type, body=body)

    def _parse_param(self):
        name = self._expect_type("IDENTIFIER")["value"]
        type_annotation = None
        if self._match_value(":"):
            type_annotation = self._advance()["value"]
        return Param(name=name, type_annotation=type_annotation)

    def _parse_class_decl(self):
        self._expect_value("class")
        name = self._expect_type("IDENTIFIER")["value"]
        self._expect_value("{")

        members = []
        while not self._check_value("}"):
            if self._at_end():
                self._error("unterminated class body, expected '}'")
            value = self._peek()["value"]
            if value in ("var", "let"):
                members.append(self._parse_var_decl())
            elif value == "func":
                members.append(self._parse_func_decl())
            else:
                self._error("expected a field or method inside class body", self._peek())
        self._expect_value("}")
        return ClassDecl(name=name, members=members)

    def _parse_block(self):
        self._expect_value("{")
        statements = []
        while not self._check_value("}"):
            if self._at_end():
                self._error("unterminated block, expected '}'")
            statements.append(self._parse_statement())
        self._expect_value("}")
        return Block(statements=statements)

    def _parse_if(self):
        self._expect_value("if")
        self._expect_value("(")
        condition = self._parse_expression()
        self._expect_value(")")
        then_branch = self._parse_block()

        else_branch = None
        if self._match_value("else"):
            else_branch = self._parse_if() if self._check_value("if") else self._parse_block()

        return IfStmt(condition=condition, then_branch=then_branch, else_branch=else_branch)

    def _parse_while(self):
        self._expect_value("while")
        self._expect_value("(")
        condition = self._parse_expression()
        self._expect_value(")")
        body = self._parse_block()
        return WhileStmt(condition=condition, body=body)

    def _parse_for(self):
        self._expect_value("for")
        self._expect_value("(")

        init = None
        if not self._check_value(";"):
            init = self._parse_var_decl() if self._peek()["value"] in ("var", "let") \
                else self._parse_expr_statement()
        else:
            self._expect_value(";")

        condition = None
        if not self._check_value(";"):
            condition = self._parse_expression()
        self._expect_value(";")

        update = None
        if not self._check_value(")"):
            update = self._parse_expression()
        self._expect_value(")")

        body = self._parse_block()
        return ForStmt(init=init, condition=condition, update=update, body=body)

    def _parse_return(self):
        self._expect_value("return")
        value = None
        if not self._check_value(";"):
            value = self._parse_expression()
        self._expect_value(";")
        return ReturnStmt(value=value)

    def _parse_print(self):
        self._expect_value("print")
        self._expect_value("(")
        value = self._parse_expression()
        self._expect_value(")")
        self._expect_value(";")
        return PrintStmt(value=value)

    def _parse_expr_statement(self):
        expr = self._parse_expression()
        self._expect_value(";")
        return ExprStmt(expression=expr)

    # ---------- expressions (lowest to highest precedence) ----------

    def _parse_expression(self):
        return self._parse_assignment()

    def _parse_assignment(self):
        if self._check_type("IDENTIFIER") and self._check_value("=", offset=1):
            name = self._advance()["value"]
            self._advance()  # consume '='
            value = self._parse_assignment()
            return Assignment(target=name, value=value)
        return self._parse_equality()

    def _parse_equality(self):
        left = self._parse_comparison()
        while self._check_value("==") or self._check_value("!="):
            op = self._advance()["value"]
            right = self._parse_comparison()
            left = BinaryOp(left=left, operator=op, right=right)
        return left

    def _parse_comparison(self):
        left = self._parse_additive()
        while self._check_value("<") or self._check_value(">") \
                or self._check_value("<=") or self._check_value(">="):
            op = self._advance()["value"]
            right = self._parse_additive()
            left = BinaryOp(left=left, operator=op, right=right)
        return left

    def _parse_additive(self):
        left = self._parse_multiplicative()
        while self._check_value("+") or self._check_value("-"):
            op = self._advance()["value"]
            right = self._parse_multiplicative()
            left = BinaryOp(left=left, operator=op, right=right)
        return left

    def _parse_multiplicative(self):
        left = self._parse_unary()
        while self._check_value("*") or self._check_value("/"):
            op = self._advance()["value"]
            right = self._parse_unary()
            left = BinaryOp(left=left, operator=op, right=right)
        return left

    def _parse_unary(self):
        if self._check_value("-") or self._check_value("+"):
            op = self._advance()["value"]
            operand = self._parse_unary()
            return UnaryOp(operator=op, operand=operand)
        return self._parse_call()

    def _parse_call(self):
        """Parses a primary expression, then any trailing '(...)' calls
        and/or '.member' accesses, chained left-to-right. Examples:
          greet("World")        -> FunctionCall
          rex.name              -> MemberAccess
          rex.speak()           -> MethodCall
          rex.speak().toUpper() -> MethodCall(MethodCall(...))  (chains work too)
        """
        expr = self._parse_primary()

        while True:
            if isinstance(expr, Identifier) and self._check_value("("):
                self._advance()
                args = self._parse_arguments()
                self._expect_value(")")
                expr = FunctionCall(callee=expr.name, arguments=args)

            elif self._check_value("."):
                self._advance()
                member = self._expect_type("IDENTIFIER")["value"]
                if self._check_value("("):
                    self._advance()
                    args = self._parse_arguments()
                    self._expect_value(")")
                    expr = MethodCall(obj=expr, method=member, arguments=args)
                else:
                    expr = MemberAccess(obj=expr, member=member)

            else:
                break

        return expr

    def _parse_arguments(self):
        """Parses a comma-separated argument list. Caller has already
        consumed the opening '(' and is responsible for the closing ')'."""
        args = []
        if not self._check_value(")"):
            args.append(self._parse_expression())
            while self._match_value(","):
                args.append(self._parse_expression())
        return args

    def _parse_primary(self):
        tok = self._peek()
        if tok is None:
            self._error("unexpected end of input while parsing an expression")

        if tok["type"] == "NUMBER":
            self._advance()
            text = tok["value"]
            return Literal(value=float(text), literal_type="Float") if "." in text \
                else Literal(value=int(text), literal_type="Int")

        if tok["type"] == "STRING":
            self._advance()
            return Literal(value=tok["value"][1:-1], literal_type="String")  # strip quotes

        # Handle boolean literals as KEYWORD tokens (lexer emits them as KEYWORD, not IDENTIFIER)
        if tok["type"] == "KEYWORD":
            if tok["value"] == "true":
                self._advance()
                return Literal(value=True, literal_type="Bool")
            if tok["value"] == "false":
                self._advance()
                return Literal(value=False, literal_type="Bool")
            # Other keywords should not appear as primary expressions
            self._error("unexpected keyword while parsing an expression", tok)

        if tok["type"] == "IDENTIFIER":
            self._advance()
            return Identifier(name=tok["value"])

        if tok["value"] == "(":
            self._advance()
            expr = self._parse_expression()
            self._expect_value(")")
            return expr

        self._error("unexpected token while parsing an expression", tok)