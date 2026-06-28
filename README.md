### **Part 1: Team Setup Guide**

**Step 1: Clone the Code**
Pull the latest code to your local machine.

```bash
git clone https://github.com/elyzadeveraturda/ProgLang.git
```

**Step 2: Install Backend Dependencies**
We are using Python and Flask for the compiler backend. Run this command to install the required libraries securely into your active Python environment:

* **Mac/Linux:** `python3 -m pip install Flask flask-cors`
* **Windows:** `python -m pip install Flask flask-cors` *(or use `py -m pip` if `python` isn't recognized)*

**Step 3: Start the Compiler Server**
Keep this running in the background. It listens for code sent from the website.

* **Mac/Linux:** `python3 app.py`
* **Windows:** `python app.py`

Check the terminal output — it prints the port it's actually running on, e.g. `Starting MiniLang Server on http://localhost:5000`.

*(Note: if you change the port in `app.py`, you MUST also update the `fetch()` URL in `index.html` to match — they will silently stop talking to each other otherwise, with no obvious error other than every tab saying "Run the compiler first." Both files currently agree on **port 5000**.)*

**Step 4: Launch the Interface**
Open your file explorer/Finder, locate the `index.html` file inside the project folder, and simply double-click it to open it in your web browser. Click **▷ Run** to test it.

---

### **Part 2: Current Architecture**

The original single-file `compiler.py` has been split into one module per compiler phase. `compiler.py` is now just the orchestrator — it calls each module in order and assembles the JSON response `app.py` sends back to the frontend.

| File | Phase(s) | What it does |
|---|---|---|
| `lexer.py` | 2 — Lexical Analysis | Turns source text into tokens. Recognizes keywords, identifiers, strings, numbers, operators, punctuation, and `#` / `//` line comments. |
| `ast_nodes.py` | 3 | Defines the AST node types (`VarDecl`, `BinaryOp`, `IfStmt`, `ClassDecl`, etc.) that the parser builds and the interpreter walks. |
| `parser.py` | 3, 6 (syntax) | Turns the token list into an AST. Parses `var`/`let`, `func`, `class`, `if`/`else`, `while`, `for`, `return`, `print`, and expressions with normal precedence. |
| `symbol_table.py` | 4 | Scope-aware storage for variable/function/class bindings. Enforces `let` immutability. |
| `semantic.py` | 5, 7 (checking) | Type-checks the AST before anything runs — catches things like `String + Int`, undefined names, wrong argument counts. |
| `interpreter.py` | 5, 6, 8 (execution) | Actually runs the program: evaluates expressions, executes loops/conditionals, constructs objects, calls `init()`. |
| `serializer.py` | — | Converts the AST and symbol table into plain dicts so they can be sent as JSON to the `AST` / `Symbols` tabs. |
| `compiler.py` | orchestrator | Calls the above in order: lex → parse → semantic check → interpret. Catches errors from any phase and formats them for the console. |

**Language syntax supported right now:**
- Types: `Int`, `Float`, `String`, `Bool`
- Declarations: `var name: Type = value;` and `let name = value;` (immutable)
- Functions: `func name(param: Type): ReturnType { ... }`, with `return`
- Classes: `class Name { var field: Type; func init(...) { ... } }` — construction, `init()`, reading fields (`rex.name`), and calling methods (`rex.speak()`) all work
- Control flow: `if` / `else` / `else if`, `while`, `for (init; cond; update)`
- Operators: `+ - * /`, `== != < > <= >=`, unary `-`
- Comments: `# like this` or `// like this`, to end of line

**Known limitations (acceptable, but worth knowing for Q&A):**
- Fields can only be set from inside the class itself (via `init()` or other methods) — assigning a field from outside, like `rex.name = "Max";`, isn't supported. This is a deliberate scope decision, not a bug, and is arguably closer to proper encapsulation than allowing free external writes.
- The `AST` and `Symbols` tabs render whatever `serializer.py` sends back — worth a final visual check before the defense, not just the `Console` tab.