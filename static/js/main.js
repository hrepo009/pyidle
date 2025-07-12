document.addEventListener('DOMContentLoaded', function () {
    // DOM एलिमेंट्स को चुनें
    const editorContainer = document.getElementById('editor-container');
    const terminalOutput = document.getElementById('terminal');
    const runButton = document.getElementById('run-button');
    const saveButton = document.getElementById('save-button');
    const loadButton = document.getElementById('load-button');
    const themeToggleButton = document.getElementById('theme-toggle-button');

    let editor; // Monaco Editor इंस्टेंस के लिए वेरिएबल

    // Monaco Editor को लोड करने के लिए कॉन्फ़िगरेशन
    require.config({ paths: { 'vs': 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs' } });
    require(['vs/editor/editor.main'], function () {
        // एडिटर को इनिशियलाइज़ करें
        editor = monaco.editor.create(editorContainer, {
            value: 'print("Hello, Python Web IDE!")\n\nfor i in range(5):\n    print(f"Number: {i}")', // डिफ़ॉल्ट कोड
            language: 'python',
            theme: 'vs-light', // डिफ़ॉल्ट थीम
            automaticLayout: true, // कंटेनर रिसाइज़ होने पर एडिटर को एडजस्ट करें
            minimap: { enabled: true },
            fontSize: 14,
            scrollBeyondLastLine: false,
        });

        // localStorage से सेव की गई थीम को लोड करें
        loadTheme();
    });

    // फंक्शन: कोड एक्सेक्यूट करें
    async function executeCode() {
        if (!editor) return;

        const code = editor.getValue();
        terminalOutput.innerText = 'Running code...';
        terminalOutput.classList.remove('error');

        try {
            const response = await fetch('/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code: code }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            // आउटपुट या एरर को टर्मिनल में दिखाएं
            if (result.error) {
                terminalOutput.innerText = result.error;
                terminalOutput.classList.add('error');
            } else {
                terminalOutput.innerText = result.output;
            }
        } catch (e) {
            terminalOutput.innerText = `Failed to connect to the server: ${e.message}`;
            terminalOutput.classList.add('error');
        }
    }

    // फंक्शन: थीम को टॉगल करें (लाइट/डार्क)
    function toggleTheme() {
        const body = document.body;
        body.classList.toggle('dark-mode');
        
        const isDarkMode = body.classList.contains('dark-mode');
        const newTheme = isDarkMode ? 'vs-dark' : 'vs-light';
        const newIcon = isDarkMode ? '☀️' : '🌙';
        
        // Monaco एडिटर की थीम बदलें
        if (editor) {
            monaco.editor.setTheme(newTheme);
        }
        
        // बटन का आइकन बदलें
        themeToggleButton.innerText = newIcon;

        // थीम को localStorage में सेव करें ताकि पेज रीलोड होने पर याद रहे
        localStorage.setItem('ide-theme', newTheme);
    }

    // फंक्शन: पेज लोड पर थीम सेट करें
    function loadTheme() {
        const savedTheme = localStorage.getItem('ide-theme') || 'vs-light';
        if (savedTheme === 'vs-dark') {
            document.body.classList.add('dark-mode');
            themeToggleButton.innerText = '☀️';
        } else {
            document.body.classList.remove('dark-mode');
            themeToggleButton.innerText = '🌙';
        }

        if (editor) {
            monaco.editor.setTheme(savedTheme);
        }
    }

    // फंक्शन: कोड को localStorage में सेव करें
    function saveCode() {
        if (!editor) return;
        const code = editor.getValue();
        localStorage.setItem('python-code-snippet', code);
        alert('Code saved successfully!');
    }

    // फंक्शन: localStorage से कोड लोड करें
    function loadCode() {
        if (!editor) return;
        const savedCode = localStorage.getItem('python-code-snippet');
        if (savedCode) {
            editor.setValue(savedCode);
            alert('Code loaded successfully!');
        } else {
            alert('No saved code found.');
        }
    }

    // इवेंट लिस्नर्स
    runButton.addEventListener('click', executeCode);
    themeToggleButton.addEventListener('click', toggleTheme);
    saveButton.addEventListener('click', saveCode);
    loadButton.addEventListener('click', loadCode);
    
    // कीबोर्ड शॉर्टकट (Ctrl+Enter or Cmd+Enter) कोड चलाने के लिए
    editorContainer.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            executeCode();
        }
    });

    // Split.js को इनिशियलाइज़ करें ताकि पैनल रिसाइज़ हो सकें
    Split(['#editor-container', '#output-container'], {
        sizes: [70, 30], // प्रारंभिक साइज़ (70% एडिटर, 30% टर्मिनल)
        minSize: 100, // न्यूनतम साइज़
        gutterSize: 8,
        cursor: 'col-resize',
        direction: 'horizontal', // डेस्कटॉप पर हॉरिजॉन्टल स्प्लिट
    });
});
