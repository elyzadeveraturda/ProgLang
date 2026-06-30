# 20-Minute Live Demo Script
## MiniLang IDE — Actual Demonstration
### 4 Presenters | Target runtime: ~20:00

**How to use this script:** This script assumes you are screen-recording
the actual MiniLang IDE running in a browser, connected to your Flask
backend. Each section tells you exactly what to click, type, or run.
Leave 2–3 seconds of silence after clicking "Run" so the recording shows
the console actually populate — don't talk over the output appearing.

**Before recording:** make sure `python3 app.py` is running in a
terminal with the venv activated, and `index.html` is open in the
browser, pointed at `localhost:5000`.

---

## SECTION 1 — Introduction & IDE Tour
**Speaker: Person 1 | Time: 0:00–2:30**

> "Hi everyone, in this video we'll actually demonstrate MiniLang running
> end-to-end. We've pre-loaded three example programs directly into the
> IDE — one for basic data types and functions, one for object-oriented
> features, and one for control flow — so you can see the full feature
> set without us typing everything live. Let's start with a quick tour
> of the interface."

**[ON SCREEN: show the IDE. Point out, while talking, without clicking
yet:]**
- The editor panel on the left labeled `main.ml` (or `editor.ml`)
- The "Run" button
- The four output tabs: Console, Tokens, AST, Symbols
- The three example buttons: Basics, OOP, Logic/Control Flow

> "On the right, we have four tabs. Console shows the result of running
> the program — including any compiler errors. Tokens shows the literal
> output of our lexical analyzer. AST shows the parsed syntax tree as a
> collapsible structure. And Symbols shows every variable, function, and
> class our semantic analyzer tracked, along with its type and whether
> it's mutable."

---

## SECTION 2 — Demo 1: Basics (Data Types, Variables, Functions)
**Speaker: Person 1 | Time: 2:30–6:30**

> "Let's start with our first pre-loaded example — Basics."

**[ON SCREEN: click the "Basics" example button. The editor populates.]**

> "This program declares four variables — a String, an Int, a Float, and
> a Bool — and defines a function called `greet` that takes a String
> parameter and returns a String, concatenating it into a greeting. Let's
> run it."

**[ON SCREEN: click "Run". Wait for output to populate. Do not talk
during this pause.]**

> "In the Console tab, you can see our compiler ran through every phase
> in order: lexical analysis completed and reported how many tokens it
> found, syntax analysis completed and reported the number of top-level
> statements, semantic analysis passed with no type errors, and then the
> program actually executed and printed its result — 'Hello from
> MiniLang!' — followed by confirmation the program finished."

**[ON SCREEN: click the "Tokens" tab.]**

> "Switching to the Tokens tab, you can see every single token our lexer
> extracted from that source code — keywords like `var` and `func`,
> identifiers, string and number literals, and punctuation. Notice the
> Line column — every token now knows exactly which line it came from,
> which is what powers accurate error messages. We can also check this
> box to hide punctuation tokens like semicolons and braces, if we just
> want to focus on the meaningful ones."

**[ON SCREEN: toggle "Hide punctuation tokens" checkbox on, then off
again.]**

**[ON SCREEN: click the "AST" tab.]**

> "Here's our Abstract Syntax Tree. Each of these collapsible nodes
> represents one construct in the program — you can see the VarDecl
| nodes for our four variables, and the FuncDecl node for `greet`,
> which itself contains nested nodes for its parameter and its return
> statement. This tree is exactly what our parser builds, and it's
> exactly what our semantic analyzer and interpreter both walk through
> afterward."

**[ON SCREEN: expand a couple of the AST nodes to show the nesting.]**

**[ON SCREEN: click the "Symbols" tab.]**

> "And finally, the Symbols tab shows our symbol table's contents after
> semantic analysis — `name`, `version`, `pi`, `isReady`, and the
> `greet` function itself, each with its inferred type, its scope, and
> whether it's mutable. Since these were all declared with `var`, they
> show as mutable; if we'd used `let` instead, this would say 'No'."

---

## SECTION 3 — Demo 2: Object-Oriented Features
**Speaker: Person 2 | Time: 6:30–11:30**

> "Now let's look at our second example, which demonstrates
> object-oriented programming."

**[ON SCREEN: click the "OOP" example button.]**

> "This defines a class called `Animal` with one field, `name`, and two
> methods: `init`, which acts as a constructor, and `speak`, which
> returns a greeting string built from the object's name. Below the
> class, we construct an instance called `rex` by calling
> `Animal(\"Rex\")`, then print its name field directly, and then print
> the result of calling `speak()` on it."

**[ON SCREEN: click "Run". Wait for output.]**

> "In the console, you can see the program executed successfully and
> printed 'Rex' from the direct field access, and then 'Rex says
> hello!' from the method call. This confirms our object construction,
> field access, and method dispatch are all working correctly."

**[ON SCREEN: click the "AST" tab.]**

> "If we look at the AST here, you can see the ClassDecl node containing
> both the VarDecl for the `name` field and the two FuncDecl nodes for
> `init` and `speak`, nested exactly the way they were written."

**[ON SCREEN: click the "Symbols" tab.]**

> "And in the Symbols tab, notice that `Animal` and `rex` both appear at
> global scope — `Animal` is shown as a class, and is not mutable,
> since you can't reassign a class declaration."

> "One implementation detail worth highlighting: our methods don't use
> an explicit `self` keyword. When `speak()` runs, the interpreter
> pre-loads the instance's fields directly into that function call's
> local scope, so the method body can reference `name` directly instead
> of writing `self.name`. This was a deliberate simplification for
> readability in a teaching language, while still keeping each object's
> data properly encapsulated."

---

## SECTION 4 — Demo 3: Control Flow
**Speaker: Person 3 | Time: 11:30–15:30**

> "Our third example demonstrates control flow — conditionals and
> loops."

**[ON SCREEN: click the "Logic" or "Control Flow" example button.]**

> "This program declares an integer `x` starting at zero, then runs a
> while-loop that continues as long as `x` is less than five. Inside the
> loop, an if-statement checks whether `x` equals three, and if so,
> prints 'Halfway!'. After the if-statement, `x` is incremented by one
> each iteration."

**[ON SCREEN: click "Run". Wait for output.]**

> "Looking at the console, the loop ran correctly — we see 'Halfway!'
> printed exactly once, which confirms the if-condition only triggered
> on the one iteration where `x` was actually equal to three, and the
> loop terminated cleanly once `x` reached five."

> "Let's also demonstrate something not in this example by default —
> our logical operators. I'll add a line here using `and`."

**[ON SCREEN: live-type an additional line into the editor, for example:]**
```
if (x > 0 and x < 10) {
    print("x is in range");
}
```

> "Let's run this modified version."

**[ON SCREEN: click "Run". Wait for output.]**

> "And you can see 'x is in range' printed as well, confirming our
> `and` operator correctly requires both sides to be true. We also
> support `or` and `not` with proper short-circuit evaluation, meaning
> the second operand of an `and` is never even evaluated if the first
> one is already false."

---

## SECTION 5 — Error Handling Demonstration
**Speaker: Person 3 | Time: 15:30–18:00**

> "Before we wrap up, let's intentionally demonstrate how MiniLang
> handles errors, since catching mistakes before runtime is one of the
> core goals of a statically-typed language."

**[ON SCREEN: clear the editor and type a small program with a clear
syntax error, for example removing a semicolon:]**
```
var x: Int = 5
print(x);
```

> "Notice I removed the semicolon after the variable declaration. Let's
> run this."

**[ON SCREEN: click "Run". Wait for output.]**

> "You can see our parser caught this immediately and reported a
> Syntax Error, including the exact line number where the problem
> occurred — line 1 — rather than a vague or confusing message."

**[ON SCREEN: fix the semicolon, then introduce a type error instead,
for example:]**
```
var x: Int = 5;
var y: Bool = x;
```

> "Now let's try a type mismatch — assigning an Int to a variable
> explicitly declared as a Bool."

**[ON SCREEN: click "Run". Wait for output.]**

> "And here, semantic analysis catches it — a Type Error explaining that
> we can't assign an Int to a variable of type Bool. This demonstrates
> that our compiler performs real type checking, not just syntax
> validation — these two are genuinely separate phases, and you can see
> both of them reporting independently in the console."

---

## SECTION 6 — Closing
**Speaker: Person 4 | Time: 18:00–20:00**

> "To wrap up, we've shown three working programs covering basic data
> types and functions, object-oriented class definitions with
> constructors and methods, and control flow with conditionals, loops,
> and logical operators — along with our compiler correctly catching
> both syntax and type errors before a program ever executes.
>
> Everything you've seen runs through the same five-phase pipeline:
> lexical analysis, syntax analysis, semantic analysis, and execution,
> all wrapped in a browser-based IDE we built to make the entire process
> visible and inspectable at every stage — not just a black box that
> either works or doesn't.
>
> Thank you for watching our demonstration of MiniLang."

**[ON SCREEN: end on the IDE with the Basics example still loaded, or
fade to a closing slide with your group's names.]**

---

## Pacing Notes
- Total: 20:00 across 6 sections.
- The biggest risk for running long is Section 5 (Error Handling) —
  if you're tight on time, you can demonstrate only ONE error type
  (either syntax or semantic) instead of both, and still satisfy the
  rubric's request for "how it works."
- Always pause in silence for 2-3 seconds after clicking Run before
  speaking again — this looks far more natural on video than narrating
  over a loading state.
- If your screen recording software supports it, zoom in on the code
  editor while typing the live examples in Sections 4 and 5 so small
  text (like `and`, `==`, semicolons) is clearly readable.
- Test your full demo flow once, start to finish, without recording,
  to make sure the Flask server doesn't time out or need a restart
  partway through.
