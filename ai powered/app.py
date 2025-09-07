import joblib
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import PyPDF2
import io

# Create Flask app
app = Flask(__name__)
CORS(app)

# Load the trained model and vectorizer
try:
    model = joblib.load('career_predictor.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
    print("Model and vectorizer loaded successfully.")
except FileNotFoundError:
    print("Error: Model or vectorizer file not found. Make sure they are in the 'ai powered' directory.")
    model = None
    vectorizer = None

# HTML template for the root page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Career Predictor</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; text-align: center; }
        form { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        textarea { width: 100%; height: 150px; padding: 8px; }
        button { background: #4CAF50; color: white; padding: 10px 15px; border: none; cursor: pointer; }
        button:hover { background: #45a049; }
        #result { margin-top: 20px; padding: 15px; background: #e7f3fe; border-left: 6px solid #2196F3; }
    </style>
</head>
<body>
    <h1>AI Career Predictor</h1>
    <p>Enter your skills or paste your resume text below to get a career prediction.</p>
    
    <form id="predictionForm">
        <div class="form-group">
            <label for="userInput">Skills/Resume Text:</label>
            <textarea id="userInput" name="userInput" placeholder="e.g., Python, Machine Learning, Data Analysis, SQL..."></textarea>
        </div>
        <button type="submit">Predict Career</button>
    </form>
    
    <div id="result" style="display: none;"></div>
    
    <script>
        document.getElementById('predictionForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const text = document.getElementById('userInput').value;
            if (!text) {
                alert('Please enter some text about your skills or experience.');
                return;
            }
            
            const resultDiv = document.getElementById('result');
            resultDiv.textContent = 'Analyzing...';
            resultDiv.style.display = 'block';
            
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ text: text })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.textContent = `Predicted Career: ${data.predicted_career}`;
                } else {
                    resultDiv.textContent = `Error: ${data.error || 'Something went wrong'}`;
                }
            } catch (error) {
                resultDiv.textContent = `Error: ${error.message}`;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/predict', methods=['POST'])
def predict():
    if not model or not vectorizer:
        return jsonify({'error': 'Model not loaded'}), 500

    if 'file' in request.files:
        file = request.files['file']
        if file.filename.endswith('.pdf'):
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            except Exception as e:
                return jsonify({'error': f"Error processing PDF: {e}"}), 400
        else:
            text = file.read().decode('utf-8')
    elif 'text' in request.json:
        text = request.json['text']
    else:
        return jsonify({'error': 'No text or file provided'}), 400

    # Vectorize the input text and make a prediction
    vectorized_text = vectorizer.transform([text])
    prediction = model.predict(vectorized_text)

    return jsonify({'predicted_career': prediction[0]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
