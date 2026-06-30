"""
lexer.py
Lexical Analysis — Phase 2.

CHANGES FROM ORIGINAL:
  1. Added 'and', 'or', 'not' as KEYWORD tokens so logical operators work.
  2. Tokens now carry a 'line' field so error messages can say "line 5".
"""

import re


class LexerError(Exception):
    pass


TOKEN_SPECIFICATION = [
    ('COMMENT',    r'(#|//).*'),
    # CHANGE 1: added 'and', 'or', 'not' to the keyword list
    ('KEYWORD',    r'\b(let|print|func|return|var|String|Int|Float|Bool|'
                   r'if|else|while|for|class|true|false|and|or|not)\b'),
    ('IDENTIFIER', r'[A-Za-z_][A-Za-z0-9_]*'),
    ('STRING',     r'".*?"'),
    ('NUMBER',     r'\d+(\.\d+)?'),
    ('EQ',         r'==|!=|<=|>='),
    ('ASSIGN',     r'='),
    ('OP',         r'[+\-*/<>]'),
    ('PUNCT',      r'[;{}(),:.]'),
    ('SKIP',       r'[ \t\n]+'),
    ('MISMATCH',   r'.'),
]

_TOKEN_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION)


def tokenize(source_code):
    """Returns a list of {"type", "value", "line"} dicts.
    CHANGE 2: each token now has a 'line' key so parsers and error
    messages can report which line a problem is on."""
    tokens = []
    line_num = 1  # CHANGE 2: track current line number

    for match in re.finditer(_TOKEN_REGEX, source_code):
        kind = match.lastgroup
        value = match.group()

        # CHANGE 2: count newlines in whitespace/comment spans to keep
        # line_num accurate even across multi-line gaps.
        if kind == 'SKIP':
            line_num += value.count('\n')
            continue
        if kind == 'COMMENT':
            continue
        if kind == 'MISMATCH':
            raise LexerError(f"Lexical Error (line {line_num}): Unexpected character '{value}'")

        if kind == 'EQ':
            kind = 'OP'

        # CHANGE 2: store the line number on every token
        tokens.append({"type": kind, "value": value, "line": line_num})

    return tokens
