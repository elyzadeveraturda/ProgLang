

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
*(Note: If you get an "Address already in use" error, let the team know, and we can switch the port in `app.py` and `index.html` from 5000 to 5001).*

**Step 4: Launch the Interface**
Open your file explorer/Finder, locate the `index.html` file inside the project folder, and simply double-click it to open it in your web browser. Click **▷ Run** to test the Lexical Analyzer!

---

### **Part 2: Project Enhancements (What to Build Next)**

Right now, the app successfully performs **Phase 2 (Lexical Analysis)** by breaking strings into tokens. To make sure everything is rock-solid for your upcoming project defense, here are the exact features the team needs to build into `compiler.py` next to hit your rubric requirements:

**1. Build the Parser (Syntax Analysis - Phase 3)**

* **Current State:** We just have a flat list of tokens.
* **Enhancement:** Write a function that loops through the tokens and builds an Abstract Syntax Tree (AST). For example, it needs to recognize that `var x = 5;` is a "Variable Declaration Statement" containing an identifier (`x`) and a value (`5`).

**2. Implement the Environment (Scope & Binding - Phase 4)**

* **Current State:** Variables aren't actually saved anywhere.
* **Enhancement:** Create a Python dictionary (a "Symbol Table") in the backend that stores variable names and their current values. This is essential so that if a user types `let x = 10; print(x);`, the compiler remembers what `x` is.

**3. Add Semantic Execution & Math (Phase 5 & 7)**

* **Current State:** The code is scanned, but no math or logic actually runs.
* **Enhancement:** Write an evaluator that traverses the AST. If it sees an addition operation (`+`) between two `Int` tokens, it should execute the math in Python and prepare the result to send back to the frontend console.

**4. Graceful Error Handling**

* **Current State:** Only basic lexical errors are caught.
* **Enhancement:** Add `try/except` blocks in the Parser and Evaluator. If a user tries to add a String to an Int, or calls a variable that doesn't exist, the backend should catch it and send a clean, formatted red error message to the frontend console (exactly like the one in your original screenshot).
