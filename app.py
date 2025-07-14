import os
import subprocess
import sys
import re
from flask import Flask, request, jsonify, render_template

# Flask एप्लिकेशन को इनिशियलाइज़ करें
app = Flask(__name__, template_folder='templates', static_folder='static')

# कोड रन टाइम लिमिट
CODE_EXECUTION_TIMEOUT = 5  # सेकंड

# खतरनाक कीवर्ड्स की लिस्ट
DANGEROUS_KEYWORDS = [
    "import os", "import sys", "import subprocess", "import socket",
    "import shutil", "open(", "eval(", "exec(", "input(", "__import__",
    "compile(", "globals(", "locals(", "exit(", "quit(", "del ",
    "pickle", "marshal", "thread", "multiprocessing", "ctypes", "signal",
    "memoryview", "fork", "os.system", "system(", "Popen"
]

def is_dangerous_code(code: str) -> bool:
    """
    कोड में खतरनाक कीवर्ड्स की जाँच करता है।
    """
    lower_code = code.lower()
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in lower_code:
            return True
    return False
@app.route('/')
def index():
    """
    मुख्य पेज को रेंडर करता है।
    """
    return render_template('index.html')

@app.route('/how-to-use')
def howTOUse():
    """
    How to Use पेज को रेंडर करता है।
    """
    return render_template('how-to-use.html')

@app.route('/legal')
def legal():
    """
    Term And Privacy पेज को रेंडर करता है।
    """
    return render_template('legal.html')

@app.route('/execute', methods=['POST'])
def execute_code():
    """
    यूज़र का कोड प्राप्त करता है, उसे सुरक्षित रूप से रन करता है,
    और आउटपुट या एरर भेजता है।
    """
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({'error': 'Invalid request. "code" field is missing.'}), 400

    code = data['code']

    # खतरनाक कोड की जाँच
    if is_dangerous_code(code):
        return jsonify({
            'output': '',
            'error': 'Your code contains restricted or unsafe commands. Execution denied for safety.'
        }), 400

    python_executable = sys.executable

    try:
        completed_process = subprocess.run(
            [python_executable, '-c', code],
            capture_output=True,
            text=True,
            timeout=CODE_EXECUTION_TIMEOUT,
            check=True
        )
        output = completed_process.stdout
        return jsonify({'output': output, 'error': ''})

    except subprocess.TimeoutExpired:
        return jsonify({
            'output': '',
            'error': f'Execution timed out! Code took longer than {CODE_EXECUTION_TIMEOUT} seconds to run.'
        })

    except subprocess.CalledProcessError as e:
        error_output = e.stderr
        return jsonify({'output': '', 'error': error_output})

    except Exception as e:
        return jsonify({'output': '', 'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    # Flask ऐप को रन करें
    app.run(debug=True, host='0.0.0.0', port=5000)
