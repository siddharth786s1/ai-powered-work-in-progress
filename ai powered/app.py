import joblib
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import PyPDF2
import io
import re
import docx

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

# Helper function to extract skills from text
def extract_skills_from_text(text):
    # This is a mock implementation. A real-world app would use NLP for this.
    # For now, we'll find words that are likely skills
    known_skills = [
        'python', 'java', 'javascript', 'html', 'css', 'react', 'node', 'sql', 
        'mongodb', 'django', 'flask', 'aws', 'azure', 'git', 'docker', 'kubernetes',
        'machine learning', 'data analysis', 'data science', 'ai', 'nlp',
        'communication', 'teamwork', 'leadership', 'project management',
        'marketing', 'sales', 'customer service', 'excel', 'powerpoint', 'word'
    ]
    words = set(re.findall(r'\b\w+\b', text.lower()))
    found_skills = [skill for skill in known_skills if skill in ' '.join(words).lower()]
    
    # Add some capitalized words as potential skills
    other_potential_skills = re.findall(r'\b[A-Z][a-z]{2,}\b', text)[:3]
    return list(set(found_skills + other_potential_skills))

# Helper function to extract text from different file types
def extract_text_from_file(file):
    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        return "".join(page.extract_text() for page in pdf_reader.pages)
    elif file.filename.endswith('.docx'):
        doc = docx.Document(io.BytesIO(file.read()))
        return "\n".join(para.text for para in doc.paragraphs)
    elif file.filename.endswith('.txt'):
        return file.read().decode('utf-8')
    else:
        raise ValueError("Unsupported file format")

# HTML template for the root page - Using Tailwind CSS
HTML_TEMPLATE = """
<!-- AI-Powered Career Path Recommender Frontend -->
<!-- Uses Tailwind CSS CDN for styling and modern JS for logic -->

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AI-Powered Career Path Recommender</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen flex flex-col">
  <header class="bg-blue-600 text-white py-6 shadow">
    <h1 class="text-3xl font-bold text-center">AI-Powered Career Path Recommender</h1>
    <p class="text-center mt-2">Discover your ideal career path with AI-driven recommendations</p>
  </header>
  <main class="flex-1 flex flex-col items-center justify-center px-4">
    <!-- File Upload Section -->
    <section class="w-full max-w-md bg-white rounded-lg shadow p-6 mt-8">
      <h2 class="text-xl font-semibold mb-4">Upload Your Resume</h2>
      <input id="resumeInput" type="file" accept=".pdf,.doc,.docx,.txt"
        class="block w-full mb-4 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
      <button id="analyzeBtn" disabled
        class="w-full bg-blue-600 text-white py-2 rounded font-semibold transition disabled:opacity-50 hover:bg-blue-700">
        Analyze
      </button>
      <!-- Loading Spinner -->
      <div id="spinner" class="flex justify-center mt-4 hidden">
        <svg class="animate-spin h-8 w-8 text-blue-600" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
          <path class="opacity-75" fill="currentColor"
            d="M4 12a8 8 0 018-8v8z"/>
        </svg>
      </div>
      <!-- Message Box -->
      <div id="messageBox" class="mt-4 hidden px-4 py-2 rounded bg-blue-100 text-blue-800 text-center"></div>
    </section>
    <!-- Results Section -->
    <section id="resultsSection" class="w-full max-w-2xl mt-10 hidden">
      <h2 class="text-xl font-semibold mb-4">Extracted Skills</h2>
      <ul id="skillsList" class="mb-6 flex flex-wrap gap-2"></ul>
      <h2 class="text-xl font-semibold mb-4">Recommended Careers</h2>
      <div id="recommendations" class="space-y-4"></div>
    </section>
  </main>
  <footer class="bg-gray-200 text-center py-4 mt-auto">
    <span class="text-gray-600">© 2025 AI Career Path Recommender</span>
  </footer>
  <script>
    // Elements
    const resumeInput = document.getElementById('resumeInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const spinner = document.getElementById('spinner');
    const messageBox = document.getElementById('messageBox');
    const resultsSection = document.getElementById('resultsSection');
    const skillsList = document.getElementById('skillsList');
    const recommendationsDiv = document.getElementById('recommendations');

    // Backend API base URL - using direct paths instead of /api prefix
    const API_BASE = "";

    // Enable button when file is selected
    resumeInput.addEventListener('change', () => {
      analyzeBtn.disabled = !resumeInput.files.length;
    });

    // Show custom message box
    function showMessage(msg, type = "info") {
      messageBox.textContent = msg;
      messageBox.className = `mt-4 px-4 py-2 rounded text-center ${
        type === "error" ? "bg-red-100 text-red-800" : "bg-blue-100 text-blue-800"
      }`;
      messageBox.style.display = "block";
    }

    // Hide message box
    function hideMessage() {
      messageBox.style.display = "none";
    }

    // Show/hide spinner
    function showSpinner() { spinner.style.display = "flex"; }
    function hideSpinner() { spinner.style.display = "none"; }

    // Display extracted skills
    function displaySkills(skills) {
      skillsList.innerHTML = "";
      skills.forEach(skill => {
        const li = document.createElement('li');
        li.textContent = skill;
        li.className = "bg-blue-200 text-blue-800 px-3 py-1 rounded-full text-sm";
        skillsList.appendChild(li);
      });
    }

    // Display career recommendations
    function displayRecommendations(recommendations) {
      recommendationsDiv.innerHTML = "";
      recommendations.forEach(rec => {
        const div = document.createElement('div');
        div.className = "bg-white rounded shadow p-4";
        div.innerHTML = `
          <h3 class="text-lg font-bold mb-2">${rec.title}</h3>
          <p class="mb-1">Match Score: <span class="font-semibold text-blue-600">${rec.match_score}%</span></p>
          <p class="mb-1">Skills to Improve: ${
            rec.missing_skills.length
              ? rec.missing_skills.map(s => `<span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs mr-1">${s}</span>`).join('')
              : '<span class="text-green-600 font-semibold">None! You are a great fit.</span>'
          }</p>
        `;
        recommendationsDiv.appendChild(div);
      });
    }

    // Main analyze flow
    analyzeBtn.addEventListener('click', async () => {
      hideMessage();
      resultsSection.style.display = "none";
      showSpinner();
      analyzeBtn.disabled = true;
      showMessage("Analyzing resume...");

      // Step 1: Upload resume and get skills
      const formData = new FormData();
      formData.append('file', resumeInput.files[0]);
      let skills;
      try {
        const res = await fetch(`/api/upload_resume`, {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        if (!res.ok || !data.skills) throw new Error(data.error || "Failed to extract skills.");
        skills = data.skills;
      } catch (err) {
        showMessage("Error extracting skills: " + err.message, "error");
        hideSpinner();
        analyzeBtn.disabled = false;
        return;
      }

      // Step 2: Get career recommendations
      showMessage("Fetching career recommendations...");
      let recommendations;
      try {
        const res = await fetch(`/api/recommend`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ skills }),
        });
        const data = await res.json();
        if (!res.ok || !data.recommendations) throw new Error(data.error || "Failed to get recommendations.");
        recommendations = data.recommendations;
      } catch (err) {
        showMessage("Error fetching recommendations: " + err.message, "error");
        hideSpinner();
        analyzeBtn.disabled = false;
        return;
      }

      // Step 3: Display results
      hideSpinner();
      showMessage("Recommendations ready!");
      displaySkills(skills);
      displayRecommendations(recommendations);
      resultsSection.style.display = "block";
      analyzeBtn.disabled = false;
    });
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/upload_resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        text = extract_text_from_file(file)
        skills = extract_skills_from_text(text)
        return jsonify({'skills': skills})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/recommend', methods=['POST'])
def recommend():
    if not model or not vectorizer:
        return jsonify({'error': 'Model not loaded'}), 500
    
    data = request.json
    if not data or 'skills' not in data:
        return jsonify({'error': 'No skills provided'}), 400
    
    # Join skills into a single text for the model
    text = ', '.join(data['skills'])
    
    # Vectorize the input text and make a prediction
    try:
        vectorized_text = vectorizer.transform([text])
        prediction = model.predict(vectorized_text)[0]
        
        # Try to get probabilities if the model supports it
        probabilities = None
        try:
            probabilities = model.predict_proba(vectorized_text)[0]
            top_indices = probabilities.argsort()[-3:][::-1]  # Top 3 predictions
            top_careers = model.classes_[top_indices]
            top_scores = probabilities[top_indices]
            
            # Create recommendations with match scores and missing skills
            recommendations = []
            for career, score in zip(top_careers, top_scores):
                # Generate random missing skills for demo purposes
                # In a real app, this would be determined by analyzing the requirements for each career
                missing_skills = []
                if score < 0.9:
                    if 'python' not in data['skills'] and career == 'Data Scientist':
                        missing_skills.append('Python')
                    if 'machine learning' not in data['skills'] and career == 'Data Scientist':
                        missing_skills.append('Machine Learning')
                    if 'java' not in data['skills'] and career == 'Software Engineer':
                        missing_skills.append('Java')
                    if 'communication' not in data['skills'] and career == 'Business Analyst':
                        missing_skills.append('Communication')
                
                recommendations.append({
                    'title': career,
                    'match_score': int(score * 100),
                    'missing_skills': missing_skills
                })
            
            return jsonify({'recommendations': recommendations})
            
        except:
            # Fallback if predict_proba isn't available
            return jsonify({'recommendations': [
                {
                    'title': prediction,
                    'match_score': 85,
                    'missing_skills': ['Teamwork', 'Project Management']
                }
            ]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    """Legacy endpoint for backward compatibility"""
    if not model or not vectorizer:
        return jsonify({'error': 'Model not loaded'}), 500

    if 'file' in request.files:
        file = request.files['file']
        try:
            text = extract_text_from_file(file)
        except Exception as e:
            return jsonify({'error': f"Error processing file: {e}"}), 400
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
