# compiler.py
import re

def run_mini_compiler(source_code):
    # Phase 2: Lexical Analysis (Simplified)
    token_specification = [
        ('KEYWORD',   r'\b(let|print|func|return|var|String|Int|Float|Bool)\b'),
        ('IDENTIFIER',r'[A-Za-z_][A-Za-z0-9_]*'),
        ('STRING',    r'".*?"'),
        ('NUMBER',    r'\d+(\.\d+)?'),
        ('ASSIGN',    r'='),
        ('OP',        r'[+\-*/==<>]'),
        ('PUNCT',     r'[;{}(),:]'),
        ('SKIP',      r'[ \t\n]+'),
        ('MISMATCH',  r'.'),
    ]
    
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    tokens = []
    console_output = []
    error = None

    try:
        # Scan tokens
        for mo in re.finditer(tok_regex, source_code):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise Exception(f"Lexical Error: Unexpected character '{value}'")
            tokens.append({"type": kind, "value": value})
            
        console_output.append(f"✓ Lexical analysis complete — {len(tokens)} tokens")
        
        # TODO: Add Phase 3 (Parser) and Phase 5 (Semantic Execution) here later.
        
    except Exception as e:
        error = str(e)
        console_output.append(f"✗ {error}")

    # Return the data as a dictionary so Flask can send it as JSON
    return {
        "console": "\n".join(console_output),
        "tokens": tokens,
        "error": error
    }
