# errors.py

class CompilerError(Exception):
    """
    Base class for all MiniLang compiler errors.
    """

    phase = "Compiler"

    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(message)

    def __str__(self):
        location = ""

        if self.line is not None:
            location += f" (line {self.line}"

            if self.column is not None:
                location += f", column {self.column}"

            location += ")"

        return f"{self.phase} Error: {self.message}{location}"


class LexerError(CompilerError):
    phase = "Lexical"


class ParserError(CompilerError):
    phase = "Syntax"


class SemanticError(CompilerError):
    phase = "Semantic"


class SymbolTableError(CompilerError):
    phase = "Scope"


class RuntimeError(CompilerError):
    phase = "Runtime"

class OOPError(CompilerError):
    phase = "OOP"