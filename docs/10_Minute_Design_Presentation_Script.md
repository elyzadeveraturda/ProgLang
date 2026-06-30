# 10-Minute Design & Development Presentation Script
## MiniLang — A Mini Programming Language
### 4 Presenters | Target runtime: ~10:00

**How to use this script:** Each section lists the speaker, a suggested
time budget, what to say, and what to show on screen (your code editor,
slides, or the running IDE). Practice with a timer at least twice —
groups almost always run long on Phase explanations, so keep examples
short and let the screen do the talking.

---

## SECTION 1 — Introduction & Language Purpose
**Speaker: Person 1 | Time: 0:00–1:30**

> "Good [morning/afternoon], we're presenting MiniLang, a statically-typed
> mini programming language we designed and implemented from scratch,
> covering everything from lexical analysis to object-oriented features.
>
> MiniLang's purpose is educational: it's a small, C-like language meant
> to demonstrate how a real compiler pipeline works — tokenizing source
> code, parsing it into a syntax tree, checking it for type and scope
> errors, and finally executing it — all built from the ground up rather
> than relying on an existing parser generator or framework.
>
> We chose a syntax that feels familiar to anyone who's used JavaScript,
> Swift, or TypeScript: curly-brace blocks, semicolons, optional type
> annotations like `var x: Int`, and `let` for immutable bindings versus
> `var` for mutable ones. We'll walk through how each phase of our
> compiler pipeline was designed, then hand off to our actual demo video
| right after this."

**[ON SCREEN: title slide, then briefly show the running IDE with Example
1 already loaded, but don't run it yet]**

---

## SECTION 2 — Lexical Analysis (Phase 2)
**Speaker: Person 1 | Time: 1:30–2:45**

> "The first phase is lexical analysis — turning raw source text into a
> flat list of tokens. Our lexer is built around a single regular
> expression made up of named groups: one pattern for comments, one for
> keywords, one for identifiers, strings, numbers, and operators.
>
> A key design decision here was operator ordering. Multi-character
> operators like `==`, `!=`, `<=`, and `>=` have to be checked *before*
> single-character ones, otherwise `==` would incorrectly tokenize as two
> separate `=` tokens. We also made sure every token carries its source
> line number, so later phases — like the parser and semantic analyzer —
> can report errors like 'Syntax Error on line 5' instead of just
> pointing at a vague problem somewhere in the file."

**[ON SCREEN: show lexer.py's TOKEN_SPECIFICATION list briefly, highlight
the EQ pattern ordered before ASSIGN/OP]**

---

## SECTION 3 — Syntax Analysis & Grammar (Phase 3)
**Speaker: Person 2 | Time: 2:45–4:15**

> "Once we have tokens, the parser builds an Abstract Syntax Tree using
> recursive descent — a top-down parsing technique where each grammar
> rule becomes its own function. Statements like variable declarations,
> function declarations, if-statements, while-loops, and for-loops each
> have a dedicated `_parse_` method.
>
> For expressions, we implemented a precedence chain: assignment is the
> loosest-binding operation, then logical `and`/`or`/`not`, then
> equality, then comparison, then addition and subtraction, then
> multiplication and division, and finally unary operators and function
> calls bind the tightest. This chain is what makes an expression like
> `x = a + b * 2 > 0 and y` parse correctly without needing parentheses
> everywhere, the same way real languages handle operator precedence."

**[ON SCREEN: show the chain of _parse_assignment → _parse_logical →
_parse_equality → _parse_comparison → _parse_additive →
_parse_multiplicative in parser.py — just scroll through it]**

---

## SECTION 4 — Names, Scope, and Binding (Phase 4)
**Speaker: Person 2 | Time: 4:15–5:15**

> "For scope and binding, we implemented a symbol table backed by a
> stack of dictionaries. The first scope in that stack is the global
> scope, which is never popped. Entering a function body, an if-block, a
> while-loop, or a for-loop pushes a brand-new scope; leaving it pops
> that scope off, which gives us proper lexical scoping — inner blocks
> can see outer variables, but outer code can't see into inner blocks.
>
> We also distinguish `let` from `var`. A `let` binding is immutable
> after declaration — trying to reassign it raises a Name Error at
> semantic-analysis time, before the program even runs."

**[ON SCREEN: symbol_table.py — show push_scope/pop_scope and the
is_let check inside assign()]**

---

## SECTION 5 — Semantic Analysis & Data Types (Phases 5 & 7)
**Speaker: Person 3 | Time: 5:15–7:00**

> "This is really the heart of our language design. Our semantic
> analyzer walks the entire AST *before* anything executes, and performs
> type checking using four core types: Int, Float, String, and Bool.
>
> We made a deliberate design choice on type compatibility: an Int can
> be used wherever a Float is expected, since that's a safe, lossless
> widening — but the reverse isn't allowed without an explicit
> conversion. We also made string concatenation strict: the `+`
> operator only auto-concatenates String with String, or does numeric
> addition between Int and Float — it does not implicitly convert
> numbers into strings, which is a common source of subtle bugs in some
> dynamically-typed languages. If you want to print a number alongside
> text, our `print()` statement actually supports multiple comma-separated
> arguments, like `print(\"Count:\", x)`, instead of relying on string
> concatenation.
>
> Every undeclared variable, type mismatch, or wrong-arity function call
> is caught right here, before the interpreter ever touches the code —
> that's what makes this a *statically* typed language rather than one
> that only fails at runtime."

**[ON SCREEN: semantic.py — show _binary_result_type and the
KNOWN_TYPES / NUMERIC_TYPES sets]**

---

## SECTION 6 — Control Flow (Phase 6)
**Speaker: Person 3 | Time: 7:00–7:45**

> "For control flow, MiniLang supports if/else with optional else-if
> chaining, while-loops, and C-style for-loops with an initializer,
> condition, and update expression. We also added logical operators —
> `and`, `or`, and `not` — with proper short-circuit evaluation, meaning
> the right-hand side of an `and` is never evaluated if the left side is
> already false, which mirrors how every mainstream language handles
> logical operators for both correctness and performance."

**[ON SCREEN: briefly show interpreter.py's _eval_LogicalOp method with
the short-circuit early returns]**

---

## SECTION 7 — Object-Oriented Features (Phase 8)
**Speaker: Person 4 | Time: 7:45–9:00**

> "Finally, our object-oriented layer. MiniLang supports class
> declarations with fields and methods. Object construction calls an
> optional `init()` method, similar to a constructor, and instances
> store their field values in a per-object dictionary at runtime.
>
> One interesting implementation detail: methods don't use an explicit
> `self` keyword. Instead, when a method runs, we pre-load the object's
> fields directly into that call's local scope, so the method body can
> read and write fields by their bare name — and after the call
> finishes, we sync those values back onto the instance. This keeps the
> syntax simpler for a teaching language while still supporting real
> encapsulation, since fields genuinely live on the object, not in some
> shared global space."

**[ON SCREEN: interpreter.py — show _construct_instance and
_call_function's field_scope parameter]**

---

## SECTION 8 — Closing & Architecture Summary
**Speaker: Person 4 | Time: 9:00–10:00**

> "To summarize our architecture: source code flows through five
> Python modules in sequence — `lexer.py` tokenizes it, `parser.py`
> builds the AST, `semantic.py` validates types and scope, and
> `interpreter.py` actually executes the program, all orchestrated by
> `compiler.py`. Every error from any phase is caught and reported back
> in a consistent format, and we also built a browser-based IDE on top
> of this pipeline with a live console, token viewer, AST viewer, and
> symbol table viewer, which you'll see in detail in our demo video
> right after this. Thank you."

**[ON SCREEN: end on a clean diagram or just the project's file
structure — lexer.py → parser.py → semantic.py → interpreter.py]**

---

## Pacing Notes
- Total: 10:00 across 8 sections, ~75 seconds average per section.
- If you're running long in rehearsal, Section 6 (Control Flow) is the
  safest to trim — it's the most familiar concept to viewers and needs
  the least justification.
- Don't read code line-by-line on screen; scroll naturally while talking,
  the visual is supporting evidence, not the focus.
- Practice the handoffs between speakers — a one-sentence bridge like
  "Now that source code is broken into a tree, let's talk about how we
  catch errors before runtime" makes transitions feel planned rather than
  abrupt.
