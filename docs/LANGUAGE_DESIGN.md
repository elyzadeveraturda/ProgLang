# Phase 1: Language Design

## a) Purpose of the Language

**MiniLang** is a small, statically-typed, general-purpose teaching language designed to demonstrate the complete pipeline of programming language implementation — lexical analysis, syntax analysis, scope and binding, semantic analysis, control flow, data types, and object-oriented execution — within the scope of a single academic project.

Its goal isn't to be a production language; it's to be simple enough to fully build, test, and explain in a defense, while still being expressive enough to write real (if small) programs: declaring typed variables, writing functions with parameters and return values, branching and looping, and defining classes with fields and methods. Every language design decision below favors **clarity and explicitness** over convenience — e.g. mandatory type annotations and semicolons — because the point of the project is to make each compiler phase's job visible, not to optimize for typing speed.

## b) Syntax Style

### Keywords

| Category | Keywords |
|---|---|
| Declarations | `var`, `let`, `func`, `class`, `return` |
| Types | `Int`, `Float`, `String`, `Bool` |
| Control flow | `if`, `else`, `while`, `for` |
| Literals | `true`, `false` |
| I/O | `print` |

### Symbols

| Symbol | Meaning |
|---|---|
| `;` | statement terminator |
| `{ }` | block delimiters (function bodies, class bodies, control-flow bodies) |
| `( )` | grouping, function parameters, function/method call arguments |
| `:` | type annotation separator (`name: Type`) |
| `,` | separates parameters / arguments |
| `.` | member access (`rex.name`) and method calls (`rex.speak()`) |
| `=` | assignment |
| `+ - * /` | arithmetic operators |
| `== != < > <= >=` | comparison operators |
| `#` or `//` | line comment, runs to end of line |

### Design rationale

`var`/`let` mirrors Swift's mutability distinction (`let` bindings are immutable once assigned) — chosen specifically so the symbol table phase (Phase 4) has something concrete to enforce, rather than treating all variables as mutable.

Type annotations after a colon (`name: Type`) rather than before the name (`Type name`) were chosen to keep declarations visually consistent with function signatures (`func greet(who: String): String`), so a learner sees the same `name: Type` pattern everywhere in the language.

## Basic Structure of a Program

A MiniLang program is a flat sequence of top-level statements, executed top to bottom. A statement is one of:

- a variable declaration (`var` / `let`)
- a function declaration (`func`)
- a class declaration (`class`)
- a control-flow statement (`if`, `while`, `for`)
- a `print` statement
- a bare expression statement (e.g. an assignment like `x = x + 1;`)

Blocks (function bodies, class bodies, loop/conditional bodies) are delimited by `{ }` and can themselves contain any of the statement types above, allowing nesting. Every statement ends in `;` except block-bodied constructs, which end in `}`.

### Minimal example showing the structure

```
# comment
var x: Int = 0;

func isEven(n: Int): Bool {
    return n == 0;
}

class Counter {
    var value: Int;
    func init(start: Int) {
        value = start;
    }
    func increment() {
        value = value + 1;
    }
}

while (x < 3) {
    if (isEven(x)) {
        print("even");
    }
    x = x + 1;
}
```

This single example exercises every top-level statement type the rubric expects to see: a typed variable, a typed function, a class with a field and methods, and control flow.