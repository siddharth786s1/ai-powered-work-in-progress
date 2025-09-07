# AI Career Predictor

This project is a web application that leverages a pre-trained machine learning model to predict suitable career paths based on user-provided text, such as the content of a resume.

The application is built with Flask and uses a scikit-learn model to make predictions.

## Features

*   **Career Prediction**: Analyzes text to suggest potential career roles.
*   **PDF Processing**: Capable of extracting text from PDF documents (likely resumes).
*   **Web API**: Exposes the prediction functionality through a Flask-based REST API.
*   **Pre-trained Model**: Includes a pre-trained classifier (`career_predictor.pkl`) and a text vectorizer (`vectorizer.pkl`).

## Tech Stack

The core of this project is built with Python and relies on the following libraries:

*   **Flask**: For the web server and API.
*   **Flask-Cors**: To handle Cross-Origin Resource Sharing (CORS).
*   **scikit-learn**: For the machine learning model.
*   **joblib**: For loading the pre-trained model files.
*   **pandas**: For data manipulation.
*   **PyPDF2**: For reading and extracting text from PDF files.

## Setup and Installation

1.  **Clone the repository (if you haven't already):**
    ```sh
    git clone <your-repository-url>
    cd ai-powered-work-in-progress
    ```

2.  **Create a virtual environment:**
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    The dependencies are listed in the [`ai powered/requirements.txt`](ai powered/requirements.txt) file.
    ```sh
    pip install -r "ai powered/requirements.txt"
    ```

## Usage

To run the application, start the Flask web server.

Run the server:

```sh
cd "ai powered"
python app.py
```

You can then send a POST request with your resume text to the `/predict` endpoint to get a career prediction. You can either send a JSON payload with a `text` key, or a multipart form request with a `file` key containing a text or PDF file.
