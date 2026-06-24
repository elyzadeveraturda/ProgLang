# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from compiler import run_mini_compiler

app = Flask(__name__)
CORS(app) # Allows your local HTML file to access this API

@app.route('/run', methods=['POST'])
def run_code():
    # 1. Get the code from the frontend
    data = request.get_json()
    source_code = data.get('code', '')

    # 2. Pass it to your compiler logic
    result = run_mini_compiler(source_code)

    # 3. Send the results back as JSON
    return jsonify(result)

if __name__ == '__main__':
    print("Starting MiniLang Server on http://localhost:5001")
    app.run(debug=True, port=5001)
