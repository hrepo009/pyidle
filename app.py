import os
import subprocess
import sys
from flask import Flask, request, jsonify, render_template

# Flask एप्लिकेशन को इनिशियलाइज़ करें
app = Flask(__name__, template_folder='templates', static_folder='static')

# सुरक्षा चेतावनी: यह फंक्शन सीधे यूजर इनपुट को एक्सेक्यूट करता है।
# प्रोडक्शन एनवायरमेंट के लिए, इसे Docker या किसी अन्य सैंडबॉक्सिंग तकनीक के अंदर चलाना चाहिए।
# हमने सुरक्षा के लिए एक टाइमआउट जोड़ा है ताकि अनंत लूप से बचा जा सके।
CODE_EXECUTION_TIMEOUT = 5  # सेकंड में

@app.route('/')
def index():
    """
    मुख्य पेज (index.html) को रेंडर करता है।
    """
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_code():
    """
    फ्रंटएंड से Python कोड प्राप्त करता है, उसे सुरक्षित रूप से एक्सेक्यूट करता है,
    और आउटपुट या एरर वापस भेजता है।
    """
    # अनुरोध से JSON डेटा निकालें
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({'error': 'Invalid request. "code" field is missing.'}), 400

    code = data['code']

    # Python एक्सेक्यूटेबल का पाथ प्राप्त करें (वर्चुअल एनवायरमेंट के अंदर वाला)
    # यह सुनिश्चित करता है कि कोड उसी एनवायरमेंट में चले जिसमें सर्वर चल रहा है।
    python_executable = sys.executable

    try:
        # subprocess.run का उपयोग कोड को एक अलग प्रोसेस में चलाने के लिए करें
        # - 'capture_output=True' stdout और stderr को कैप्चर करता है।
        # - 'text=True' आउटपुट को स्ट्रिंग के रूप में डीकोड करता है।
        # - 'timeout' कमांड को दिए गए समय के बाद समाप्त कर देता है।
        # - 'check=True' अगर रिटर्न कोड नॉन-जीरो हो तो CalledProcessError फेंकता है।
        completed_process = subprocess.run(
            [python_executable, '-c', code],
            capture_output=True,
            text=True,
            timeout=CODE_EXECUTION_TIMEOUT,
            check=True  # अगर कोई एरर हो तो एक्सेप्शन रेज़ करेगा
        )
        
        # अगर कोड सफलतापूर्वक चला
        output = completed_process.stdout
        return jsonify({'output': output, 'error': ''})

    except subprocess.TimeoutExpired:
        # अगर कोड निर्धारित समय में पूरा नहीं होता है
        return jsonify({
            'output': '',
            'error': f'Execution timed out! Code took longer than {CODE_EXECUTION_TIMEOUT} seconds to run.'
        })
        
    except subprocess.CalledProcessError as e:
        # अगर कोड एक्सेक्यूट होते समय कोई एरर आता है (जैसे सिंटैक्स एरर)
        # stderr में एरर मैसेज होता है
        error_output = e.stderr
        return jsonify({'output': '', 'error': error_output})
        
    except Exception as e:
        # अन्य अप्रत्याशित एरर को हैंडल करने के लिए
        return jsonify({'output': '', 'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    # ऐप को डीबग मोड में चलाएं।
    # प्रोडक्शन के लिए, gunicorn या uWSGI जैसे WSGI सर्वर का उपयोग करें।
    app.run(debug=True, host='0.0.0.0', port=5000)
