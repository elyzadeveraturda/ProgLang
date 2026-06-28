"""
lexer.py
Lexical Analysis — Phase 2.

Scans raw MiniLang source text into a flat list of tokens. This is the
tokenizer that used to live inline in compiler.py — moved here so
parser.py (and later semantic.py / interpreter.py) can import it directly.

Token format is unchanged: {"type": ..., "value": ...} dicts.

Two fixes vs. the original inline version:
  1. Multi-character operators (==, !=, <=, >=) are matched BEFORE the
     single-character ones, so "==" is one token, not two ASSIGN tokens.
  2. if / else / while / for / class / true / false are now KEYWORD
     tokens instead of falling through to IDENTIFIER.
"""

import re


class LexerError(Exception):
    """Raised on an unrecognized character. Same message format as
    before: 'Lexical Error: ...'"""
    pass


TOKEN_SPECIFICATION = [
    ('COMMENT',    r'(#|//).*'),
    ('KEYWORD',    r'\b(let|print|func|return|var|String|Int|Float|Bool|'
                   r'if|else|while|for|class|true|false)\b'),
    ('IDENTIFIER', r'[A-Za-z_][A-Za-z0-9_]*'),
    ('STRING',     r'".*?"'),
    ('NUMBER',     r'\d+(\.\d+)?'),
    ('EQ',         r'==|!=|<=|>='),   # multi-char comparisons, checked first
    ('ASSIGN',     r'='),
    ('OP',         r'[+\-*/<>]'),     # '=' removed — ASSIGN/EQ own it now
    ('PUNCT',      r'[;{}(),:.]'),    # '.' added, ready for MemberAccess later
    ('SKIP',       r'[ \t\n]+'),
    ('MISMATCH',   r'.'),
]

_TOKEN_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION)


def tokenize(source_code):
    """Returns a list of {"type", "value"} dicts. Raises LexerError on
    the first unrecognized character."""
    tokens = []
    for match in re.finditer(_TOKEN_REGEX, source_code):
        kind = match.lastgroup
        value = match.group()

        if kind in ('SKIP', 'COMMENT'):
            continue
        if kind == 'MISMATCH':
            raise LexerError(f"Lexical Error: Unexpected character '{value}'")

        # Normalize EQ into OP — parser.py only needs to check one type
        # for all comparison operators (==, !=, <, >, <=, >=).
        if kind == 'EQ':
            kind = 'OP'

        tokens.append({"type": kind, "value": value})

    return tokens