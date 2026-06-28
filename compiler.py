"""
compiler.py
Orchestrator — wires Phase 2 through Phase 8 together.

Calls each phase in order: lexer -> parser -> semantic analysis ->
interpreter. Errors from any phase are caught and sent to the frontend
console in the same "✓ ..." / "✗ ..." format the lexer originally used.
"""

from lexer import tokenize, LexerError
from parser import Parser, ParserError
from semantic import SemanticAnalyzer, SemanticError
from interpreter import Interpreter, RuntimeError
from symbol_table import SymbolTableError
from serializer import ast_to_dict



def run_mini_compiler(source_code):
    console_output = []
    tokens = []
    ast = None
    error = None
    semantic_analyzer = None

    try:
        # Phase 2: Lexical Analysis
        tokens = tokenize(source_code)
        console_output.append(f"✓ Lexical analysis complete — {len(tokens)} tokens")

        # Phase 3: Syntax Analysis
        ast = Parser(tokens).parse()
        console_output.append(
            f"✓ Syntax analysis complete — {len(ast.statements)} top-level statement(s)"
        )

        # Phase 4 + 5 + 7: Scope/Binding, Semantic Analysis, Data Types
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.check(ast)
        console_output.append("✓ Semantic analysis complete")

        # Phase 5 + 6 + 8: Execution, Control Flow, OOP
        program_output = Interpreter().run(ast)
        console_output.extend(program_output)   # each print() statement's output, in order
        console_output.append("✓ Program executed")

    except (LexerError, ParserError, SemanticError, SymbolTableError, RuntimeError) as e:
        error = str(e)
        console_output.append(f"✗ {error}")
    except Exception as e:
        # Catch-all so an unexpected bug never crashes the Flask request.
        error = f"Internal Error: {e}"
        console_output.append(f"✗ {error}")

    # Extract symbols from semantic analysis if successful
    symbols = []
    if error is None and ast is not None:
        try:
            semantic_analyzer = SemanticAnalyzer()
            symbol_table = semantic_analyzer.check(ast)
            symbols = symbol_table.to_dict()
        except Exception:
            # If symbol extraction fails, just return empty list
            symbols = []

    return {
        "success": error is None,
        "console": console_output,
        "tokens": tokens,
        "ast": ast_to_dict(ast),
        "symbols": symbols,
        "error": error
    }   